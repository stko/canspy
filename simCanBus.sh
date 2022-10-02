BAUDRATE=250000
sudo modprobe can
sudo modprobe can_raw
sudo modprobe can_bcm
sudo modprobe vcan
#sudo ip link add dev vcan0 type vcan
#sudo ip link set up vcan0
sudo ip link set can0 type can bitrate $BAUDRATE
sudo ip link set up can0
sudo ip link set can1 type can bitrate $BAUDRATE
sudo ip link set up can1

