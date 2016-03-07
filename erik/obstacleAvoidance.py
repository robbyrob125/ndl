import sys
import math

from naoqi import ALProxy

NAO_IP = "nao.local"
NAO_PORT = 9559

subscriptions = []

def getProxy(robotIP, proxy):
    try:
        p = ALProxy("AL" + proxy, robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ", proxy
        print "Error was: ", e
        return None
    return p

def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)
    
def setup(robotIP):
    speech = getProxy(robotIP, "SpeechRecognition")
    try:
        speech.unsubscribe('WordRecognized')
    except:
        pass
    speech.setVocabulary(['hello', 'walk', 'find','turn', 'stand', 'sit'], False)
    speech.subscribe('WordRecognized')
    subscriptions.append((speech, 'WordRecognized'))
    
lastWord = None
def getWord(robotIP, memory):
    global lastWord
    words = memory.getData("WordRecognized")
    if words != lastWord:
        lastWord = words
        try:
            if words[1] > 0.4:
                return words[0]
        except:
            pass
    return None
    
def avoid(robotIP):
    # Init proxies.
    setup(robotIP)
    
    tts = getProxy(robotIP, 'TextToSpeech')
    posture = getProxy(robotIP, 'RobotPosture')
    motion = getProxy(robotIP, 'Motion')
    navigation = getProxy(robotIP, 'Navigation')
    memory = getProxy(robotIP, "Memory")

    # Set NAO in stiffness On
    StiffnessOn(motion)
    posture.goToPosture("StandInit", 0.5)
    
    while True:
        word = getWord(robotIP, memory)
        if word == 'hello':
            tts.say('Hello!')
        elif word == 'stand':
            posture.goToPosture("StandInit", 0.5)
        elif word == 'walk':
            tts.say('AAAAAAAH')
            posture.stopMove()
            navigation.moveTo(0.5, 0.0, 0.0)
        elif word == 'sit':
            tts.say('Sitting')
            posture.stopMove()
            posture.goToPosture("Sit", 0.5)
        elif word == 'turn':
            #posture.goToPosture("StandInit", 0.5)
            tts.say('Turning')
            posture.stopMove()
            navigation.moveTo(0.0, 0.0, math.pi)
        elif word == 'find':
            posture.stopMove()
            posture.goToPosture("StandInit", 0.5)
            findCamil(robotIP)
        elif word != None:
            tts.say("Sorry, I don't understand")
            time.sleep(0.5)
    
    # Will stop at 0.5m (FRAME_ROBOT) instead of 0.4m away from the obstacle.
    #navigation.setSecurityDistance(0.01)
    
    # No specific move config.
    #navigation.moveTo(1.0, 0.0, 0.0)
    

    # To do 6 cm steps instead of 4 cm.
    #navigation.moveTo(0.0, 0.0, 1.0, [["MaxStepX", 0.04]])
    
    #tts.say("I found a wall")
    
    
    #led.rasta(15000)
    
    
    #tts.say("I finally found you!")

if __name__ == '__main__':
    try:
        avoid(NAO_IP)
    except KeyboardInterrupt:
        pass
    except Exception, e:
        print('ERRRRRRRRRRRRRRRRRRRRRRRRRR')
        print(e)
    
    for proxy, event in subscriptions:
        proxy.unsubscribe(event)

    print('Goodbye')

