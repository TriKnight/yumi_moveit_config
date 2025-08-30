# yumi.launch.py
#
# Top-level launch file to start YuMi control + MoveIt2 together
#

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    # Paths to the sub-launch files
    yumi_control_launch = PathJoinSubstitution(
        [FindPackageShare("yumi_moveit_config"), "launch", "yumi_control.launch.py"]
    )

    yumi_moveit_launch = PathJoinSubstitution(
        [FindPackageShare("yumi_moveit_config"), "launch", "yumi_moveit.launch.py"]
    )

    # Include both
    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(yumi_control_launch)
    )

    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(yumi_moveit_launch)
    )

    return LaunchDescription([control_launch, moveit_launch])

