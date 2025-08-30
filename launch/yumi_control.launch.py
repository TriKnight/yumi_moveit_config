# yumi_control.launch.py
#
# Bring up YuMi dual-arm with ros2_control and MoveIt2
#

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_arguments = []

    # Arguments
    declared_arguments.append(
        DeclareLaunchArgument(
            "runtime_config_package",
            default_value="yumi_moveit_config",
            description="Package with controller configuration (config folder).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "controllers_file",
            default_value="yumi_controllers.yaml",
            description="YAML file with the controllers configuration.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_package",
            default_value="yumi_description",
            description="Description package with URDF/XACRO files.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_file",
            default_value="yumi.urdf",
            description="URDF description file for YuMi.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_package",
            default_value="yumi_moveit_config",
            description="MoveIt configuration package for YuMi.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "prefix",
            default_value='""',
            description="Prefix for joint names (multi-robot setups).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="true",
            description="Start robot with fake hardware (for simulation).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_sensor_commands",
            default_value="false",
            description="Enable fake sensor command interfaces (only with fake hardware).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "initial_joint_controller",
            default_value="right_arm_controller",
            description="Which joint controller to start initially.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "launch_rviz", default_value="false", description="Launch RViz?"
        )
    )

    # Initialize Arguments
    runtime_config_package = LaunchConfiguration("runtime_config_package")
    controllers_file = LaunchConfiguration("controllers_file")
    description_package = LaunchConfiguration("description_package")
    moveit_config_package = LaunchConfiguration("moveit_config_package")
    description_file = LaunchConfiguration("description_file")
    prefix = LaunchConfiguration("prefix")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    fake_sensor_commands = LaunchConfiguration("fake_sensor_commands")
    initial_joint_controller = LaunchConfiguration("initial_joint_controller")
    launch_rviz = LaunchConfiguration("launch_rviz")

    # Robot Description
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution([FindPackageShare(description_package), "urdf", description_file]),
            " ",
            "prefix:=",
            prefix,
            " ",
            "use_fake_hardware:=",
            use_fake_hardware,
            " ",
            "fake_sensor_commands:=",
            fake_sensor_commands,
            " ",
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    # Controllers YAML
    robot_controllers = PathJoinSubstitution(
        [FindPackageShare(runtime_config_package), "config", controllers_file]
    )

    # RViz config
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare(moveit_config_package), "config", "moveit.rviz"]
    )

    # Nodes
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="both",
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    rviz_node = Node(
        package="rviz2",
        condition=IfCondition(launch_rviz),
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
    )

    # Spawners
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
    )

    # Spawn initial joint controller (defaults to right_arm_controller)
    initial_joint_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[initial_joint_controller, "-c", "/controller_manager"],
    )

    # Explicit spawner for left_arm_controller (always load)
    left_arm_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_arm_controller", "-c", "/controller_manager"],
    )

    left_gripper_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["left_gripper_controller", "-c", "/controller_manager"],
    )

    right_gripper_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["right_gripper_controller", "-c", "/controller_manager"],
    )

    return LaunchDescription(
        declared_arguments
        + [
            control_node,
            robot_state_publisher_node,
            rviz_node,
            joint_state_broadcaster_spawner,
            initial_joint_controller_spawner,
            left_arm_spawner,   # ✅ added
            left_gripper_spawner,
            right_gripper_spawner,
        ]
    )

