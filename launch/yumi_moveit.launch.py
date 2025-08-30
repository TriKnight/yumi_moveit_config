import os
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)

    try:
        with open(absolute_file_path, "r") as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None


def launch_setup(context, *args, **kwargs):
    # Arguments
    robot_xacro_file = LaunchConfiguration("robot_xacro_file")
    support_package = LaunchConfiguration("support_package")
    moveit_config_package = LaunchConfiguration("moveit_config_package")
    moveit_config_file = LaunchConfiguration("moveit_config_file")

    # Build MoveIt config
    moveit_config = (
        MoveItConfigsBuilder("yumi", package_name=moveit_config_package.perform(context))
        .robot_description(
            file_path=os.path.join(
                get_package_share_directory(support_package.perform(context)),
                "urdf",
                robot_xacro_file.perform(context),
            )
        )
        .robot_description_semantic(
            file_path=os.path.join(
                get_package_share_directory(moveit_config_package.perform(context)),
                "config",
                moveit_config_file.perform(context),
            )
        )
        .planning_pipelines()
        .robot_description_kinematics(
            file_path=os.path.join(
                get_package_share_directory(moveit_config_package.perform(context)),
                "config",
                "kinematics.yaml",
            )
        )
        .trajectory_execution(
            file_path=os.path.join(
                get_package_share_directory(moveit_config_package.perform(context)),
                "config",
                "moveit_controllers.yaml",
            )
        )
        .planning_scene_monitor(
            publish_planning_scene=True,
            publish_geometry_updates=True,
            publish_state_updates=True,
            publish_transforms_updates=True,
            publish_robot_description=True,
            publish_robot_description_semantic=True,
        )
        .joint_limits(
            file_path=os.path.join(
                get_package_share_directory(moveit_config_package.perform(context)),
                "config",
                "joint_limits.yaml",
            )
        )
        .to_moveit_configs()
    )

    # MoveIt controllers
    moveit_controllers = {
        "moveit_simple_controller_manager": load_yaml(
            moveit_config_package.perform(context), "config/moveit_controllers.yaml"
        ),
        "moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager",
    }

    # move_group node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.trajectory_execution,
            moveit_controllers,
            moveit_config.to_dict(),
        ],
    )

    # RViz with MoveIt config
    rviz_config = os.path.join(
        get_package_share_directory(moveit_config_package.perform(context)),
        "config",
        "moveit.rviz",
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[moveit_config.to_dict()],
    )

    # Static TF world → base_link
    static_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
    )

    # Publish robot state
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[moveit_config.robot_description,
         moveit_config.robot_description_semantic,],
    )

    return [move_group_node, rviz_node, static_tf_node, robot_state_pub_node]


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_xacro_file",
            default_value="yumi.urdf",
            description="URDF/Xacro describing YuMi robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "support_package",
            default_value="yumi_description",
            description="Package containing URDF/Xacro",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_package",
            default_value="yumi_moveit_config",
            description="MoveIt config package for YuMi",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_file",
            default_value="yumi.srdf",
            description="SRDF file for YuMi",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])

