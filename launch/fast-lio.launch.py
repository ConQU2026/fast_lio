import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    fast_lio_path = get_package_share_directory('fast_lio')
    livox_driver_path = get_package_share_directory('livox_ros_driver2')

    fast_lio_rviz_config_path = os.path.join(
        fast_lio_path, 'rviz', 'fastlio.rviz')

    fast_lio_config_file = os.path.join(
        fast_lio_path, 'config', 'mid360.yaml'
    )
    livox_driver_launch_path = os.path.join(
        livox_driver_path, 'launch_ROS2', 'msg_MID360_launch.py'
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

    livox_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(livox_driver_launch_path)
    )

    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(livox_driver_launch)
    ld.add_action(fast_lio_node)
    ld.add_action(rviz_node)

    return ld
