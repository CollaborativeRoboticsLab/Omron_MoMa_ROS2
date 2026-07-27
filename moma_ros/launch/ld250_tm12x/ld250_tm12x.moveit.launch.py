import os
import sys
import yaml
import json
import xacro
from launch import LaunchDescription
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

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)

    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except OSError:  # parent of IOError, OSError *and* WindowsError where available
        return None
        
def generate_launch_description():
    # Configure robot_description
    robot_description_config = xacro.process_file(
        os.path.join(
            get_package_share_directory('moma_description'),
            'xacro',
            'ld250_tm12x.urdf.xacro',
        )
    )
    robot_description = {'robot_description': robot_description_config.toxml()}


    # SRDF Configuration
    robot_description_semantic_config = load_file('ld250_tm12x_moveit_config', 'config/ld250_tm12x.srdf')
    robot_description_semantic = {'robot_description_semantic': robot_description_semantic_config}

    # Kinematics
    kinematics_yaml = load_yaml('tm12x_moveit_config'  , 'config/kinematics.yaml')
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}


    # Planning Configuration
    ompl_planning_pipeline_config = {
        'planning_pipelines': ['ompl', 'pilz_industrial_motion_planner', 'chomp'],
        'default_planning_pipeline': 'ompl',
        'ompl': load_yaml('tm12x_moveit_config', 'config/ompl_planning.yaml'),
        'pilz_industrial_motion_planner': load_yaml(
            'tm12x_moveit_config', 'config/pilz_industrial_motion_planner_planning.yaml'
        ),
        'chomp': load_yaml('tm12x_moveit_config', 'config/chomp_planning.yaml'),
    }

    # Trajectory Execution Configuration -> Controllers
    moveit_controllers = load_yaml('tm12x_moveit_config', 'config/moveit_controllers.yaml')

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
    joint_limits = load_yaml('tm12x_moveit_config', 'config/joint_limits.yaml')
    joint_limits.update(load_yaml('tm12x_moveit_config', 'config/pilz_cartesian_limits.yaml'))
    joint_limits_yaml = {'robot_description_planning': joint_limits}

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

    # Virtual Hand Solo to Base Link  Static TF
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        output='log',
        arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'base_link', 'base']
    )

    return LaunchDescription([
        run_move_group_node,
        static_tf_node
        ])

    
