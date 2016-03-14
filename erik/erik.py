import sys
import time
import traceback

from naoqi import ALProxy

NAO_IP = "nao.local"
NAO_PORT = 9559

subscriptions = []

def StiffnessOn(proxy):
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def getProxy(robotIP, proxy):
    try:
        p = ALProxy("AL" + proxy, robotIP, 9559)
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
    
def setup(ip):
    mark = getProxy(ip, 'LandMarkDetection')
    motion = getProxy(ip, 'Motion')
    posture = getProxy(ip, 'RobotPosture')
    awareness = getProxy(ip, 'BasicAwareness')
    speech = getProxy(ip, "SpeechRecognition")

    for stimulus in ['Sound', 'Movement', 'People', 'Touch']:
        awareness.setStimulusDetectionEnabled(stimulus, False)
    awareness.setEngagementMode('SemiEngaged')
    awareness.setTrackingMode('MoveContextually')

    subscribe(mark, 'LandMarks', 500, 0.0)

    # Stand
    StiffnessOn(motion)
    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

    for part in ['Body', 'Head', 'Legs', 'Arms']:
        motion.setIdlePostureEnabled(part, False)
        motion.setBreathEnabled(part, False)
    motion.setAngles(['Head'], [0.0,0.0], 0.8)
    motion.setSmartStiffnessEnabled(True)
    
    speech.setVocabulary(['kitchen', 'room'], False)

def follow(ip, goal, ascending=True):
    mark = getProxy(ip, 'LandMarkDetection')
    mem = getProxy(ip, 'Memory')
    tts = getProxy(ip, 'TextToSpeech')
    motion = getProxy(ip, 'Motion')
    posture = getProxy(ip, 'RobotPosture')
    tracker = getProxy(ip, 'Tracker')
    awareness = getProxy(ip, 'BasicAwareness')

    current = 0 if ascending else 1000

    while True:
        try:
            data = mem.getData('LandmarkDetected')
            print(data)

            detected = []
            marks = data[1]
            for [[_,alpha,beta,_,_,heading], [mark]] in marks:
                if mark > current and ascending or \
                        mark < current and not ascending:
                    detected.append((mark,alpha,beta,heading))

            print(detected)
            
            if len(detected) > 1:
                print("I'm totally confused")
            elif len(detected) == 1:
                mark, alpha, beta, heading = detected[0]

                current = mark

                awareness.stopAwareness()

                tracker.registerTarget('LandMark', [0.1, [mark]])
                tracker.setMaximumDistanceDetection(1000)
                tracker.setMode('Move')
                tracker.track('LandMark')
                tracker.setRelativePosition([-0.3, 0.0, 0.0, 0.1, 0.1, 0.3])
                tts.say("%d" % mark)

                while tracker.isActive() and not tracker.isTargetLost():
                    print(tracker.getMode())
                    time.sleep(1)

                result = 'lost' if tracker.isTargetLost() else 'done'
                tts.say(result)
                print(result)
                
                tracker.stopTracker()
                awareness.startAwareness()

            if current == goal:
                return

        except (IndexError, TypeError):
            pass

        time.sleep(0.3)

def main(ip):
    mark = getProxy(ip, 'LandMarkDetection')
    mem = getProxy(ip, 'Memory')
    tts = getProxy(ip, 'TextToSpeech')
    motion = getProxy(ip, 'Motion')
    posture = getProxy(ip, 'RobotPosture')
    tracker = getProxy(ip, 'Tracker')
    awareness = getProxy(ip, 'BasicAwareness')
    speech = getProxy(ip, "SpeechRecognition")

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
   
    tracker = getProxy(NAO_IP, 'Tracker')
    tracker.stopTracker()
    tracker.unregisterAllTargets()

    print; print('Goodbye'); print

