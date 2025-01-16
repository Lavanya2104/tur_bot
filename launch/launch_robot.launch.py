import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch.event_handlers import OnProcessStart
def generate_launch_description():
    package_name = 'tur_bot'

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true'}.items()
    )

    # Load robot controller parameters
    controller_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'my_controllers.yaml')
   
    # Controller manager for robot control
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[controller_params_file],
        remappings=[('~/robot_description', '/robot_description')]
    )
   
    # Add delay before starting controller manager
    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    # Spawning the diff drive controller
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"]
    )
    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    # Spawning the joint broadcaster
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"]
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )
    # # Keyboard-based teleop control
    # teleop_twist_keyboard_node = Node(
    #     package="teleop_twist_keyboard",
    #     executable="teleop_twist_keyboard",
       
    #     output="screen"
        
    # )

    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        #diff_drive_spawner,
        delayed_diff_drive_spawner,
        #joint_broad_spawner,
        delayed_joint_broad_spawner
        # teleop_twist_keyboard_node,  # Add keyboard teleop node
    ])