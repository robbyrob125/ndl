# Erik

Nao butler

[Nao][nao] is a 58cm humanoid robot developed by [Aldebaran][aldebaran]. In this project we developed software which enables Erik, our Nao robot, to bring small objects from one place to the other.

## Implementation overview

The user should place an object in a bag that can be carried by the Nao. Other than that, carrying of objects is outside the scope of this project.

Recognising landmarks, a kind of simple QR code, is a feature built in to Nao. Since every landmark encodes a unique numerical ID, it is possible to place the landmarks in order on the path the Nao should follow between A and B. Then, depending on its destination, the Nao can track landmarks in ascending or descending order, until it reaches the minimum or maximum landmark.

For the moment, the minimum and maximum landmark are hard coded. Also the voice commands 'Kitchen' and 'Room' to start walking are hard coded. This is just a proof of concept.

Basically, the Nao is in rest mode until it receives a voice command. When it receives a command, it will start searching for landmarks. It will then track any landmark it can see, as long as it has an ID higher or lower (depending on the search mode) than the landmark last seen. When the Nao reaches the highest or lowest landmark, it stops and waits for a new command.

## Installation

You should have a Nao robot with version 2.1.4.13 of the NaoQi framework installed. Earlier versions of Erik are tested using NaoQi 2.1.3.13, so this version may work as well.

Nao runs an SSH server on port 22 by default. Mount its home directory using SSHfs by adding this to `/etc/fstab`:

    nao@192.168.1.159:/home/nao /mnt/nao fuse.sshfs noauto,_netdev,users,idmap=user,uid=1000,reconnect,allow_root 0 0

and then running:

    # mkdir /mnt/nao
    # mount /mnt/nao

The default password is `nao`.

Clone our repository (or copy the source code):

    # cd /mnt/nao
    # git clone https://github.com/robbyrob125/ndl

Unfortunately, the default software on the Nao does not include git, nor does it have a package manager to install it. So, in order to use git we have to run it on the SSHfs, which can be slow at times.

## Prepping the environment

You should print out the Nao landmarks you want to use. You can download some from [the Aldebaran website][naomark], however, for a full set you need the Nao installation CD.

Place the landmarks on Nao eye height on the path the robot should follow, such that at any place on the path it can see the next mark. Place the Nao somewhere where it can see some landmark (which does not matter).

## Executing

Then, SSH into the nao and run the butler software:

    $ ssh nao@192.168.1.159
    ... on the Nao:
    $ python ~/ndl/erik/erik.py

## Automatic Execution

To automatically run the Erik software on startup, edit `/home/nao/naoqi/preferences/autoload.ini` to include:

    [python]
    /home/nao/ndl/erik/erik.py

## Copyright

Copyright &copy; 2016 Robin Immel, Camil Staps.

[nao]:https://www.aldebaran.com/en/cool-robots/nao
[aldebaran]:https://www.aldebaran.com/
[naomark]:http://doc.aldebaran.com/2-1/_downloads/NAOmark.pdf

