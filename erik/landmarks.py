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

def main(ip):
    mark = getProxy(ip, 'LandMarkDetection')
    mem = getProxy(ip, 'Memory')
    tts = getProxy(ip, 'TextToSpeech')
    motion = getProxy(ip, 'Motion')
    posture = getProxy(ip, 'RobotPosture')
    tracker = getProxy(ip, 'Tracker')

    #subscribe(mark, 'LandMarks', 500, 0.0)

    # Stand
    StiffnessOn(motion)
    motion.wakeUp()
    posture.goToPosture("StandInit", 0.5)

    for part in ['Body', 'Head', 'Legs', 'Arms']:
        motion.setIdlePostureEnabled(part, False)
        motion.setBreathEnabled(part, False)
    motion.setAngles(['Head'], [0.0,0.0], 0.8)
    motion.setSmartStiffnessEnabled(True)

    current = 107
    tracker.registerTarget('LandMark', [0.4, [current]])
    #tracker.setMaximumDistanceDetection(1000)
    tracker.setMode('Move')
    tracker.track('LandMark')
    tts.say("%d" % current)

    while True:
        try:
            #pass
            [x, y, z] = tracker.getTargetPosition(0)
            print(x,y,z)
            if abs(x) < 0.2 and abs(y) < 0.2:
                current = 112 if current == 107 else 107
                tts.say("I'm now following mark %d." % current)
                tracker.registerTarget('LandMark', [0.4, [current]])
                tracker.track('LandMark')
        except ValueError, e:
            pass

        time.sleep(0.3)

        #detected = []
        #data = mem.getData('LandmarkDetected')
        #try:
        #    marks = data[1]
        #    for [[_,alpha,beta,_,_,heading], [mark]] in marks:
        #        detected.append((mark,alpha,beta,heading))
        #    
        #    if len(detected) > 1:
        #        print("I'm totally confused")
        #    elif len(detected) == 1:
        #        mark, alpha, beta, heading = detected[0]
        #        print("Following mark %d" % mark)
        #        motion.moveTo(0, 0, alpha)
        #        motion.moveTo(0.3, 0, 0)

        #except (IndexError, TypeError):
        #    pass

if __name__ == '__main__':
    try:
        main(NAO_IP)
    except KeyboardInterrupt:
        pass
    except:
        traceback.print_exc()

    for proxy, event in subscriptions:
        proxy.unsubscribe(event)
    
    tracker = getProxy(NAO_IP, 'Tracker')
    tracker.stopTracker()
    tracker.unregisterAllTargets()

    print; print('Goodbye'); print
