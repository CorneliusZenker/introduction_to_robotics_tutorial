#!/usr/bin/env python

import os
import yaml

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, OpaqueFunction, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, TextSubstitution
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def controller_spawning(context, *args, **kwargs):
    controllers = []

    n_robots = LaunchConfiguration('n_robots').perform(context)
    robots_file = LaunchConfiguration('robots_file').perform(context)
    use_sim_time = TextSubstitution(text='true')
    with open(robots_file, 'r') as stream:
        robots = yaml.safe_load(stream)
        
    for robot in robots[:int(n_robots)]:
        controllers.append(Node(
           package='reactive_behaviour',
           executable='controller',
           namespace=robot['name'],
           parameters=[{
            'use_sim_time': use_sim_time,
            }],
           output='screen',
        ))
        controllers.append(Node(
           package='reactive_behaviour',
           executable='scoring',
           namespace=robot['name'],
           parameters=[{
            'use_sim_time': use_sim_time,
            }],
           remappings=[('/tf', f'/{robot["name"]}/tf'), ('/tf_static', f'/{robot["name"]}/tf_static')],
           output='screen',
        ))
    
    return controllers


def generate_launch_description():
    args = {
         'behaviour': 'false',
         'world': 'icra2021_no_obstacle.world',
         'map': os.path.join(get_package_share_directory('driving_swarm_bringup'), 'maps' ,'icra2021_map_no_obstacle.yaml'),
         'robots_file': os.path.join(get_package_share_directory('driving_swarm_bringup'), 'params', 'icra2021_sim.yaml'),
         'rosbag_topics_file': os.path.join(get_package_share_directory('trajectory_follower'), 'params', 'rosbag_topics.yaml'),
         'qos_override_file': os.path.join(get_package_share_directory('experiment_measurement'), 'params', 'qos_override.yaml')
    }
    multi_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('driving_swarm_bringup'), 'launch', 'multi_robot.launch.py')),
        launch_arguments=args.items())

    ld = LaunchDescription()
    ld.add_action(multi_robot_launch)
    ld.add_action(OpaqueFunction(function=controller_spawning))
    return ld