cd /media/disk2/users/motifnet/Websites/Product/RPC-Server/
sleep 8
until /media/disk2/users/motifnet/Websites/Product/RPC-Server/start.py; do
        PIDFile="/media/disk2/users/motifnet/Websites/Product/RPC-Server/Data/pid.txt"
        echo "MotifNet Server crashed. Exit code: $?. Respawning.." >&2
        echo "Making sure process is dead. Killing by PID"
        kill -9 $(<"$PIDFile")
        echo "Deleting PID file..."
        rm /media/disk2/users/motifnet/Websites/Product/RPC-Server/Data/pid.txt 2> /dev/null
        sleep 1
done
