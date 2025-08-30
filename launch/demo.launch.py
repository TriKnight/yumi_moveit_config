# demo.launch.py
#
# Launch MoveIt2 with RViz for YuMi dual-arm robot.
#

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get paths
    pkg_yumi_description = get_package_share_directory("yumi_description")
    pkg_yumi_moveit_config = get_package_share_directory("yumi_moveit_config")

    urdf_file = os.path.join(pkg_yumi_description, "urdf", "yumi.urdf")
    srdf_file = os.path.join(pkg_yumi_moveit_config, "config", "yumi.srdf")

    kinematics_yaml = os.path.join(pkg_yumi_moveit_config, "config", "kinematics.yaml")
    ompl_yaml = os.path.join(pkg_yumi_moveit_config, "config", "ompl_planning.yaml")
    planning_yaml = os.path.join(pkg_yumi_moveit_config, "config", "planning.yaml")

    # Load files
    with open(urdf_file, "r") as f:
        robot_description_config = f.read()
    with open(srdf_file, "r") as f:
        robot_description_semantic_config = f.read()

    robot_description = {"robot_description": robot_description_config}
    robot_description_semantic = {"robot_description_semantic": robot_description_semantic_config}

    # Nodes
    rviz_config_file = os.path.join(pkg_yumi_moveit_config, "config", "moveit.rviz")

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
        parameters=[
            robot_description,
            robot_description_semantic,
            {"robot_description_kinematics": kinematics_yaml},
        ],
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    joint_state_publisher_gui = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
    )

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            {"robot_description_kinematics": kinematics_yaml},
            {"ompl": ompl_yaml},
            {"planning_pipelines": ["ompl"]},
            {"planning_scene_monitor_options": {
                "name": "planning_scene_monitor",
                "robot_description": "robot_description",
                "robot_description_semantic": "robot_description_semantic",
            }},
        ],
    )

    return LaunchDescription([
        rviz_node,
        robot_state_publisher,
        joint_state_publisher_gui,
        move_group,
    ])

