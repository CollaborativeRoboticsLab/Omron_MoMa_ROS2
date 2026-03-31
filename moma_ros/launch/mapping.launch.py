from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution

def generate_launch_description():
    slam_params = PathJoinSubstitution([FindPackageShare('moma_ros'), 'config', 'slam_params.yaml'])
    rviz_cfg    = PathJoinSubstitution([FindPackageShare('moma_ros'), 'rviz',   'mapping.rviz'])

    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            parameters=[slam_params, {'use_sim_time': False}]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_cfg],
            parameters=[{'use_sim_time': False}]
        )
    ])
