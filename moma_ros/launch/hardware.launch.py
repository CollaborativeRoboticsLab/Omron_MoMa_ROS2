import sys
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    tm_parameters = os.path.join(get_package_share_directory('tm12x_moveit_config'), 'config', 'interface.yaml')
    tm_driver_node = Node(
        package='tm_driver',
        executable='tm_driver',
        # name='tm_driver',
        output='screen',
        emulate_tty=True,
        parameters=[tm_parameters],
    )

    core_parms = os.path.join(get_package_share_directory('amr_ros'), 'config', 'parameters.yaml')
    core = Node(
        package='amr_core',
        executable='amr_core',
        name='amr_core',
        output='screen',
        parameters=[core_parms],
    )

    return LaunchDescription([
        tm_driver_node,
        core,
        ])

