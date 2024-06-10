#!/bin/bash

function check_dependencies {
	if ! [ -x "$(command -v docker-compose)" ]; then
		echo '⚠️  Error: docker-compose is not installed.' >&2
		exit 1
	fi

	if ! [ -x "$(command -v git)" ]; then
		echo '⚠️  Error: git is not installed.' >&2
		exit 1
	fi
}

function start {

	echo '🏃 Starting the containers'
	docker-compose up -d $container
}

function stop {
	echo '🛑 Stopping all containers'
	docker-compose stop
}

function teststop {
	echo '🛑 Stopping the canspy_dashboard container '
	containerid=$(docker ps -q --filter "name=canspy_dashboard")
	if [[  -z "containerid" ]]
	then
		echo "⚠️ No running canspy_dashboard container found"
		exit 1
	fi
	docker stop canspy_dashboard
	if [ ! $? -eq 0 ]; then
		echo '⚠️  Could not stop the canspy_dashboard container'
	fi

	docker rmi $containerid
	if [ ! $? -eq 0 ]; then
		echo '⚠️  Could not remove t'
	fi
}

function teststop {
	echo '🛑 Stopping the canspy_dashboard container '

	docker stop canspy_dashboard
	if [ ! $? -eq 0 ]; then
		echo '⚠️  Could not stop the canspy_dashboard container'
	fi

}


function testbuild {
	teststop
	echo '🛑 rebuild  the canspy_dashboard container '
	echo 'Search the canspy_dashboard container '
	containerid=$(docker ps -qa --filter "name=canspy_dashboard")
	if [[  -z "$containerid" ]]
	then
		echo "⚠️ No canspy_dashboard container found"
	else
		echo "remove the image"
		docker rmi $containerid
		if [ ! $? -eq 0 ]; then
			echo '⚠️  Could not remove the canspy_dashboard image'
		fi
	fi
	echo "Build the image"
	docker -D build  -t canspy_dashboard .
	if [ ! $? -eq 0 ]; then
		echo '⚠️  Could not build the canspy_dashboard image'
	else
		echo '👍  Container successfully build'
	fi

}

function teststart {
	containerid=$(docker ps -qa --filter "name=canspy_dashboard")
	if [[  -z "$containerid" ]]
	then
		echo "⚠️ No canspy_dashboard container found, so create one"
		docker run -i \
		--name canspy_dashboard \
		-v canspy_dashboard-backup:/app/devices/master/volumes/backup \
		-v canspy_dashboard-runtime:/app/devices/master/volumes/runtime \
		-v canspy_dashboard-video:/app/devices/master/volumes/videos/record_hd \
		--network=host \
		canspy_dashboard
	else
		echo "start existing container"
		docker start  -i canspy_dashboard
	fi
}



function fullbackup  {
	if [[  -z "$1" || !  -d "$1" ]]
	then
		echo "⚠️ no or invalid target directory given!: $1"
	else
		echo "start backup: copy .../volumes to $1"
		docker cp canspy_dashboard:/app/devices/master/volumes "$1"
	fi
}



function fullrestore  {
	if [[  -z "$1" || !  -d "$1" ]]
	then
		echo "⚠️ no or invalid target directory given!: $1"
	else
		echo "start backup: copy  $1 to .../volumes"
		docker cp "$1" canspy_dashboard:/app/devices/master/volumes
	fi
}


function backup  {
	if [[  -z "$1" || !  -d "$1" ]]
	then
		echo "⚠️ no or invalid target directory given!: $1"
	else
		echo "start backup: copy .../volumes/backup to $1/backup"
		docker cp canspy_dashboard:/app/devices/master/volumes/backup "$1/backup"
	fi
}



function restore  {
	if [[  -z "$1" || !  -d "$1" ]]
	then
		echo "⚠️ no or invalid target directory given!: $1"
	else
		echo "start backup: copy  $1/backup to .../volumes/backup"
		docker cp "$1/backup" canspy_dashboard:/app/devices/master/volumes/backup
	fi
}



function update {

	if [[ ! -d ".git" ]]
	then
		echo "🛑You have manually downloaded the version of canspy_dashboard.
The automatic update only works with a cloned Git repository.
Try backing up your settings shutting down all containers with 

docker-compose down --remove orphans

Then copy the current version from GitHub to this folder and run

./canspy_dashboard.sh start.

Alternatively create a Git clone of the repository."
		exit 1
	fi
	echo '☠️  Shutting down all running containers and removing them.'
	docker-compose down --remove-orphans
	if [ ! $? -eq 0 ]; then
		echo '⚠️  Updating failed. Please check the repository on GitHub.'
	fi	    
	echo '⬇️  Pulling latest release via git.'
	git fetch --tags
	latestTag=$(git describe --tags `git rev-list --tags --max-count=1`)
	git checkout $latestTag
	if [ ! $? -eq 0 ]; then
		echo '⚠️  Updating failed. Please check the repository on GitHub.'
	fi	    
	echo '⬇️  Pulling docker images.'
	docker-compose pull
	if [ ! $? -eq 0 ]; then
		echo '⚠️  Updating failed. Please check the repository on GitHub.'
	fi	    
	start
}

function login {
	echo "login into  existing container"
	docker exec -it canspy_dashboard /bin/bash
}



check_dependencies

case "$1" in
	"start")
		start
		;;
	"stop")
		stop
		;;
	"update")
		update
		;;
	"data")
		build_data_structure
		;;
	"testbuild")
		testbuild
		;;
	"teststart")
		teststart
		;;
	"teststop")
		teststop
		;;
	"fullbackup")
		fullbackup $2
		;;
	"fullrestore")
		fullrestore  $2
		;;
	"backup")
		backup  $2
		;;
	"restore")
		restore  $2
		;;
	"login")
		login
		;;
	* )
		cat << EOF
📺 canspy_dashboard – setup script
—————————————————————————————
Usage:
canspy_dashboard.sh update – update to the latest release version
canspy_dashboard.sh start – run all containers
canspy_dashboard.sh stop – stop all containers
canspy_dashboard.sh backup targetdir – backups all config data into targetdir/backup
canspy_dashboard.sh restore sourcedir – restore all config data from targetdir/backup
canspy_dashboard.sh fullbackup targetdir – backups all data, also runtime data and videos, into targetdir
canspy_dashboard.sh fullrestore sourcedir– – restores all data, also runtime data and videos, from targetdir

Check https://github.com/stko/canspy_dashboard/ for updates.
EOF
		;;
esac
