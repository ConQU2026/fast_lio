import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition

from launch_ros.actions import Node


def generate_launch_description():
    r2_spawner_path = get_package_share_directory('r2_spawner')
    joy_conventor_path = get_package_share_directory('joy_linux')

    fast_lio_path = get_package_share_directory('fast_lio')

    fast_lio_rviz_config_path = os.path.join(
        fast_lio_path, 'rviz', 'fastlio.rviz')

    fast_lio_config_file = os.path.join(
        fast_lio_path, 'config', 'mid360.yaml'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        parameters=[fast_lio_config_file,
                    {'use_sim_time': use_sim_time}],
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', fast_lio_rviz_config_path],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(fast_lio_node)
    ld.add_action(rviz_node)

    return ld
