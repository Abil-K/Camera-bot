#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
. /etc/os-release
if [[ "${ID}" != ubuntu || "${VERSION_ID}" != 24.04 ]]; then
  echo 'This installer requires Ubuntu 24.04 (ROS 2 Jazzy).'; exit 1
fi
apt-get update
apt-get install -y ca-certificates curl software-properties-common python3-venv python3-pip git v4l-utils
add-apt-repository -y universe
if ! dpkg-query -W ros2-apt-source >/dev/null 2>&1; then
  release_json=$(curl --fail --location --retry 3 https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest)
  source_version=$(printf '%s' "$release_json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])')
  source_deb=$(mktemp --suffix=.deb)
  curl --fail --location --retry 3 "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${source_version}/ros2-apt-source_${source_version}.${UBUNTU_CODENAME}_all.deb" -o "$source_deb"
  dpkg -i "$source_deb"
fi
apt-get update
apt-get install -y ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-msgs python3-colcon-common-extensions
# Ubuntu's packaged guest tools provide clipboard integration without a kernel rebuild.
apt-get install -y virtualbox-guest-utils virtualbox-guest-x11
echo 'SYSTEM_PACKAGES_READY'
