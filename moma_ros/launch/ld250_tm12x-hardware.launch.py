import sys
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)

    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        return None

def generate_launch_description():

    arm_robot_ip = LaunchConfiguration('arm_robot_ip')
    arm_use_simulation = LaunchConfiguration('arm_use_simulation')
    robot_description = LaunchConfiguration('robot_description')

    declare_robot_ip = DeclareLaunchArgument(
        'arm_robot_ip',
        default_value='192.168.1.2',
        description='Target robot IP address'
    )

    declare_use_simulation = DeclareLaunchArgument(
        'arm_use_simulation',
        default_value='false',
        description='Use simulation mode (true/false)'
    )

    declare_robot_description = DeclareLaunchArgument(
        'robot_description', 
        default={'robot_description' : load_file('moma_description', 'urdf/ld250_tm12x.urdf')},
        description='Target robot description file'
    )

    # Include tm_bringup.launch.py (arm driver bringup)
    tm_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('tm_driver'), 'launch', 'tm_bringup.launch.py')
        ),
        launch_arguments={
            'robot_ip': arm_robot_ip,
            'use_simulation': arm_use_simulation,
        }.items(),
    )

    # Include amr_core.launch.py (AMR core + robot_state_publisher)
    amr_core_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('amr_ros'), 'launch', 'amr_core.launch.py')
        ),
        launch_arguments={
            'robot_description': robot_description,
        }.items(),
    )

    # Velocity filter node
    filter = Node(
        package='moma_filter',
        executable='velocity_filter',
        name='velocity_filter',
        output='screen'
    )

    return LaunchDescription([
        declare_robot_ip,
        declare_use_simulation,
        declare_robot_description,
        tm_driver_launch,
        amr_core_launch,
        filter,
    ])
