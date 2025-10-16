import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Top-level launch args
    arm_use_simulation = LaunchConfiguration('arm_use_simulation')
    use_rviz = LaunchConfiguration('use_rviz')
    use_moveit = LaunchConfiguration('use_moveit')
    use_nav2 = LaunchConfiguration('use_nav2')

    declare_arm_use_simulation = DeclareLaunchArgument(
        'arm_use_simulation',
        default_value='false',
        description='Forwarded to hardware bringup to run arm in simulation (true/false)'
    )

    declare_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='false',
        description='Whether to start RViz (true/false)'
    )

    declare_use_moveit = DeclareLaunchArgument(
        'use_moveit',
        default_value='true',
        description='Whether to start MoveIt (true/false)'
    )

    declare_use_nav2 = DeclareLaunchArgument(
        'use_nav2',
        default_value='true',
        description='Whether to start Nav2 (true/false)'
    )

    # Paths to included launch files (within moma_ros)
    moma_ros_share = get_package_share_directory('moma_ros')
    
    include_hardware = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moma_ros_share, 'launch', 'ld250_tm12x', 'ld250_tm12x.hardware.launch.py')
        ),
        launch_arguments={
            'arm_use_simulation': arm_use_simulation,
        }.items(),
    )

    include_moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moma_ros_share, 'launch', 'ld250_tm12x', 'ld250_tm12x.moveit.launch.py')
        ),
        condition=IfCondition(use_moveit)
    )

    include_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moma_ros_share, 'launch', 'ld250_tm12x', 'ld250_tm12x.nav2.launch.py')
        ),
        condition=IfCondition(use_nav2)
    )

    include_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(moma_ros_share, 'launch', 'ld250_tm12x', 'ld250_tm12x.rviz.launch.py')
        ),
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        declare_arm_use_simulation,
        declare_use_rviz,
        declare_use_moveit,
        declare_use_nav2,
        include_hardware,
        include_moveit,
        include_nav2,
        include_rviz
    ])