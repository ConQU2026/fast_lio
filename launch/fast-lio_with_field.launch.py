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
    field_path = get_package_share_directory('rc2026_field')
    field_controller_path = get_package_share_directory('rc2026_field_controller')

    fast_lio_path = get_package_share_directory('fast_lio')


    stair_climb_config = os.path.join(
        field_controller_path, 'config', 'stair_climb_node.yaml'
    )   
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

    field_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(field_path, 'launch', 'rc2026_field_sim.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )

    r2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(r2_spawner_path, 'launch', 'spawn.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'x_pose': '4.0',
            'y_pose': '3.0',
            'z_pose': '0.04',
            'yaw': '3.14'
        }.items()
    )

    joy_conventor_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(joy_conventor_path, 'launch', 'joy_conventor_component.launch.py')
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
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

    stair_climb_node = Node(
        package='rc2026_field_controller',
        executable='stair_climb_node',
        name='stair_climb_controller',
        output='screen',
        parameters=[stair_climb_config,
                    {'use_sim_time': use_sim_time}]
    )

    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time_cmd)

    # 先启动仿真环境
    ld.add_action(field_launch)
    ld.add_action(r2_launch)
    # 再启动 joy_conventor
    ld.add_action(joy_conventor_launch)
    # 再启动 Fast-LIO
    ld.add_action(fast_lio_node)
    ld.add_action(rviz_node)
    ld.add_action(stair_climb_node)

    return ld
