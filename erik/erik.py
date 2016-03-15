import math
import sys
import time
import traceback

from naoqi import ALProxy, ALBroker, ALModule

NAO_IP = "nao.local"
NAO_PORT = 9559

Erik = None
subscriptions = []

def StiffnessOn(proxy):
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def getProxy(proxy):
    try:
        p = ALProxy("AL" + proxy)
    except Exception, e:
        print "Could not create proxy to ", proxy
        print "Error was: ", e
        return None
    return p

def subscribe(proxy, event, *pargs):
    proxy.subscribe(event, *pargs)
    subscriptions.append((proxy, event))

lastWord = None
def getWord(mem, threshold=0.4):
    global lastWord
    words = mem.getData("WordRecognized")
    if words != lastWord:
        lastWord = words
        try:
            if words[1] > threshold:
                return words[0]
        except:
            pass
    return None


class Erik(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)

        self.name = name
        print('Erik', name)

        memory = getProxy('Memory')

        #for button in ['Front', 'Middle']:
        memory.subscribeToEvent('TouchChanged', 'Erik', 'onHeadTouched')

    def onHeadTouched(self, *args):
        memory = getProxy('Memory')
        motion = getProxy('Motion')
        posture = getProxy('RobotPosture')

        print(args)

        key = 'Device/SubDeviceList/Head/Touch/%s/Sensor/Value'
        if memory.getData(key % 'Middle') == 1.0:
            motion.stopMove()
            posture.goToPosture('Stand', 0.6)
        lif memory.getData(key % 'Front') == 1.0:
            motion.stopMove()
            posture.goToPosture('Sit', 0.6)
            motion.rest()


def setup(ip):
    mark = getProxy('LandMarkDetection')
    motion = getProxy('Motion')
    posture = getProxy('RobotPosture')
    awareness = getProxy('BasicAwareness')
    speech = getProxy("SpeechRecognition")
    memory = getProxy('Memory')

    for stimulus in ['Sound', 'Movement', 'People', 'Touch']:
        awareness.setStimulusDetectionEnabled(stimulus, False)
    awareness.setEngagementMode('SemiEngaged')
    awareness.setTrackingMode('MoveContextually')

    subscribe(mark, 'LandMarks', 200, 0.0)

    # Stand
    #StiffnessOn(motion)
    motion.setSmartStiffnessEnabled(True)
    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

    for part in ['Body', 'Head', 'Legs', 'Arms']:
        motion.setIdlePostureEnabled(part, False)
        motion.setBreathEnabled(part, False)
    motion.setAngles(['Head'], [0.0,0.0], 0.8)
    motion.setSmartStiffnessEnabled(True)
    
    speech.setVocabulary(['kitchen', 'room'], False)
        
    global Erik
    Erik = Erik('Erik')

def follow(ip, goal, ascending=True):
    awareness = getProxy('BasicAwareness')
    mark = getProxy('LandMarkDetection')
    mem = getProxy('Memory')
    motion = getProxy('Motion')
    posture = getProxy('RobotPosture')
    tracker = getProxy('Tracker')
    tts = getProxy('TextToSpeech')

    current = 0 if ascending else 1000

    while True:
        if not motion.moveIsActive():
            motion.move(0.0, 0.0, math.pi / 8, [['MaxStepFrequency', 0.5]])
        try:
            data = mem.getData('LandmarkDetected')

            detected = []
            marks = data[1]
            for [[_,alpha,beta,_,_,heading], [mark]] in marks:
                if mark > current and ascending or \
                        mark < current and not ascending:
                    detected.append((mark,alpha,beta,heading))

            print(detected)
            
            if len(detected) > 1:
                print("I'm totally confused")
                tts.say("I'm totally confused")
            elif len(detected) == 1:
                mark, alpha, beta, heading = detected[0]

                awareness.stopAwareness()

                motion.stopMove()

                tracker.registerTarget('LandMark', [0.1, [mark]])
                tracker.setMaximumDistanceDetection(1000)
                tracker.setMode('Move')
                tracker.track('LandMark')
                tracker.setRelativePosition([-0.3, 0.0, 0.0, 0.1, 0.1, 0.3])
                tts.say("%d" % mark)

                while tracker.isActive() and not tracker.isTargetLost():
                    [x,y,z] = tracker.getTargetPosition(2) # robot
                    if x < 0.5 and y < 0.5:
                        break
                    print(tracker.getMode(), x, y, z)
                    time.sleep(0.3)

                lost = tracker.isTargetLost()
                result = 'lost' if lost else 'done'
                tts.say(result)
                print(result)

                if not lost:
                    current = mark
                
                tracker.stopTracker()
                awareness.startAwareness()

            if current >= goal and ascending or \
                    current <= goal and not ascending:
                return

        except (IndexError, TypeError):
            pass

        time.sleep(0.2)

def main(ip):
    broker = ALBroker('broker', '0.0.0.0', 0, ip, 9559)

    mem = getProxy('Memory')
    tts = getProxy('TextToSpeech')
    speech = getProxy("SpeechRecognition")

    setup(ip)
    subscribe(speech, 'WordRecognized')

    while True:
        word = getWord(mem)
        if word == 'kitchen':
            tts.say('Following ascending')
            speech.unsubscribe('WordRecognized')
            follow(ip, 119, True)
            subscribe(speech, 'WordRecognized')
            tts.say('Done.')
        elif word == 'room':
            tts.say('Following descending')
            speech.unsubscribe('WordRecognized')
            follow(ip, 64, False)
            subscribe(speech, 'WordRecognized')
            tts.say('Done.')
        elif word == None:
            pass
        else:
            tts.say('Sorry, what?')
    

if __name__ == '__main__':
    try:
        main(NAO_IP)
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()

    for proxy, event in subscriptions:
        try:
            proxy.unsubscribe(event)
        except:
            print("Couldn't unsubscribe from %s" % event)
   
    tracker = getProxy('Tracker')
    tracker.stopTracker()
    tracker.unregisterAllTargets()

    print; print('Goodbye'); print

