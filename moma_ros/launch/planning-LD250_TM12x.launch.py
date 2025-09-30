import os
import sys
import yaml
import json
from launch import LaunchDescription
from launch.substitutions import Command
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
    # Configure robot_description

    # robot_description_config = load_file('amr_description', 'urdf/LD250.urdf')
    robot_description_config = load_file('moma_description', 'urdf/ld250_tm12x.urdf')
    robot_description = {'robot_description' : robot_description_config}

    # SRDF Configuration
    robot_description_semantic_config = load_file('tm12x_moveit_config'  , 'config/tm12x.srdf')
    robot_description_semantic = {'robot_description_semantic': robot_description_semantic_config}

    # Kinematics
    kinematics_yaml = load_yaml('tm12x_moveit_config'  , 'config/kinematics.yaml')
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}


    # Planning Configuration
    ompl_planning_pipeline_config = {
        'planning_pipelines': ['ompl'],
        'ompl': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': """default_planner_request_adapters/AddTimeOptimalParameterization default_planner_request_adapters/FixWorkspaceBounds default_planner_request_adapters/FixStartStateBounds default_planner_request_adapters/FixStartStateCollision default_planner_request_adapters/FixStartStatePathConstraints""",
            'start_state_max_bounds_error': 0.1,
        },
    }
    ompl_planning_yaml = load_yaml('tm12x_moveit_config'  , 'config/ompl_planning.yaml')
    ompl_planning_pipeline_config['ompl'].update(ompl_planning_yaml)

    # Trajectory Execution Configuration -> Controllers
    controllers_yaml = load_yaml('tm12x_moveit_config', 'config/controllers.yaml')
    moveit_controllers = {'moveit_simple_controller_manager': controllers_yaml, 'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager'}

    # Trajectory Execution Functionality
    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.1,
    }

    # Planning scene
    planning_scene_monitor_parameters = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True,
    }

    # Joint limits
    joint_limits_yaml = {
        'robot_description_planning': load_yaml(
            'tm12x_moveit_config', 'config/joint_limits.yaml'
        )
    }

    # Start the actual move_group node/action server
    run_move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        emulate_tty=True,
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,           
            ompl_planning_pipeline_config,
            trajectory_execution,
            moveit_controllers,
            planning_scene_monitor_parameters,
            joint_limits_yaml,
            {"use_sim_time": True},
        ],
    )

    # RViz configuration
    rviz_config_file = (
        get_package_share_directory("moma_ros") + "/rviz/run_move_group.rviz"
    )

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        emulate_tty=True,
        arguments=['-d', rviz_config_file],
        parameters=[
            robot_description,
            robot_description_semantic,
            ompl_planning_pipeline_config,
            robot_description_kinematics,
            joint_limits_yaml,
        ],
    )

    # Publish TF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[robot_description]
    )

    # Joints Publisher
    joints_publisher_node = Node(
        package='amr_description',
        executable='joints_publisher',
        output='screen',
    )

    # Data Points Marker
    data_points_node = Node(
        package='amr_description',
        executable='data_points_marker',
        output='screen',
        parameters=[vis_config],
    )
        
    # Goals Marker
    goals_node = Node(
        package='amr_description',
        executable='goals_marker',
        output='screen',
    )

    # Laser Scans Marker
    laser_scans_node = Node(
        package='amr_description',
        executable='laser_scans',
        output='screen',
    )
    
    # RViz goto point node
    goto_point_node = Node(
        package='amr_core',
        executable='goto_point',
        output='screen',
    )
    
    # RViz goto point node
    localize_at_point_node = Node(
        package='amr_core',
        executable='localize_at_point',
        output='screen',
    )

    # Virtual Hand Solo to Base Link  Static TF
    static_tf_node_1 = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        output='log',
        arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'virtual_hand_solo/base_link', 'base']
    )

    # Map to Pose Static TF  
    static_tf_node_2 = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='world_publisher',
        output='log',
        arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'map', 'pose']
    )

    return LaunchDescription([
        run_move_group_node,
        rviz_node, 
        robot_state_publisher, 
        joints_publisher_node,
        data_points_node,
        goals_node,
        laser_scans_node,
        goto_point_node,
        localize_at_point_node,
        static_tf_node_1,
        static_tf_node_2
        ])

