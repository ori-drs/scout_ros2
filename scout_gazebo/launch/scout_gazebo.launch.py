import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory("scout_gazebo")
    scout_pkg = get_package_share_directory("scout_description")
    gz_pkg = get_package_share_directory("ros_gz_sim")

    urdf_file = os.path.join(pkg, "urdf", "scout_v2_sim.urdf")
    world_file = os.path.join(pkg, "worlds", "scout_world.sdf")

    with open(urdf_file, "r") as f:
        robot_description = f.read()

    resource_path = os.pathsep.join(filter(None, [
        os.path.dirname(scout_pkg),
        os.environ.get("GZ_SIM_RESOURCE_PATH", "")
    ]))

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_pkg, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={
            "gz_args": f"-r {world_file}"
        }.items()
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True
        }],
        output="screen"
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-world", "default",
            "-name", "scout_v2",
            "-string", robot_description,
            "-x", "0",
            "-y", "0",
            "-z", "0.35"
        ],
        output="screen"
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"
        ],
        output="screen"
    )

    return LaunchDescription([
        SetEnvironmentVariable(
            "GZ_SIM_RESOURCE_PATH", resource_path
        ),
        gazebo,
        robot_state_publisher,
        bridge,
        TimerAction(period=5.0, actions=[spawn_robot])
    ])
