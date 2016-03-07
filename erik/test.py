import sys

from naoqi import ALProxy

NAO_IP = "nao.local"
NAO_PORT = 9559

def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Body"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def dance(robotIP):
    # Init proxies.
    try:
        ledProxy = ALProxy("ALLeds", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALLeds"
        print "Error was: ", e

    try:
        ttsProxy = ALProxy("ALTextToSpeech", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALTextToSpeech"
        print "Error was: ", e

    try:
        motionProxy = ALProxy("ALMotion", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e

    try:
        postureProxy = ALProxy("ALRobotPosture", robotIP, 9559)
    except Exception, e:
        print "Could not create proxy to ALRobotPosture"
        print "Error was: ", e

    # Set NAO in stiffness On
    StiffnessOn(motionProxy)
    postureProxy.goToPosture("StandInit", 0.5)

    # First we defined each step
    footStepsList = []
    footStepsList.append([["LLeg"], [[0.06, 0.1, 0.0]]])
    footStepsList.append([["LLeg"], [[0.00, 0.16, 0.0]]])
    footStepsList.append([["RLeg"], [[0.00, -0.1, 0.0]]])
    footStepsList.append([["LLeg"], [[0.00, 0.16, 0.0]]])
    footStepsList.append([["RLeg"], [[-0.04, -0.1, 0.0]]])
    footStepsList.append([["RLeg"], [[0.00, -0.16, 0.0]]])
    footStepsList.append([["LLeg"], [[0.00, 0.1, 0.0]]])
    footStepsList.append([["RLeg"], [[0.00, -0.16, 0.0]]])

    # Send Foot step
    stepFrequency = 0.8
    clearExisting = False
    nbStepDance = 2 # defined the number of cycle to make

    for j in range( nbStepDance ):
        for i in range( len(footStepsList) ):
            motionProxy.setFootStepsWithSpeed(
                footStepsList[i][0],
                footStepsList[i][1],
                [stepFrequency],
                clearExisting)

    ttsProxy.say("I'm dancing")

    #ledProxy.rasta(15000)

if __name__ == '__main__':
    dance(NAO_IP)

