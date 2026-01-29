import os.path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition

from launch_ros.actions import Node


def generate_launch_description():
    # package_path = get_package_share_directory('fast_lio')
    weapon_dock_path = get_package_share_directory('rc2026_weapon_dock')
    r2_spawner_path = get_package_share_directory('r2_spawner')
    joy_conventor_path = get_package_share_directory('joy_linux')
    rc2026_field_path = get_package_share_directory('rc2026_field')

    default_config_path = os.path.join(weapon_dock_path, 'config')
    default_rviz_config_path = os.path.join(
        weapon_dock_path, 'rviz', 'only_lidar.rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_path = LaunchConfiguration('config_path')
    config_file = LaunchConfiguration('config_file')
    rviz_use = LaunchConfiguration('rviz')
    rviz_cfg = LaunchConfiguration('rviz_cfg')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_config_path_cmd = DeclareLaunchArgument(
        'config_path', default_value=default_config_path,
        description='Yaml config file path'
    )

    declare_config_file_cmd = DeclareLaunchArgument(
        'config_file', default_value='mid360.yaml',
        description='Config file'
    )
    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Use RViz to monitor results'
    )
    declare_rviz_config_path_cmd = DeclareLaunchArgument(
        'rviz_cfg', default_value=default_rviz_config_path,
        description='RViz config file path'
    )

    field_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(rc2026_field_path, 'launch', 'rc2026_field_sim_with_controller.launch.py')
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


    # fast_lio_node = Node(
    #     package='fast_lio',
    #     executable='fastlio_mapping',
    #     parameters=[PathJoinSubstitution([config_path, config_file]),
    #                 {'use_sim_time': use_sim_time}],
    #     output='screen'
    # )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_cfg],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(rviz_use)
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_config_path_cmd)
    ld.add_action(declare_config_file_cmd)
    ld.add_action(declare_rviz_cmd)
    ld.add_action(declare_rviz_config_path_cmd)

    # 先启动仿真环境
    ld.add_action(field_launch)
    ld.add_action(r2_launch)
    # 再启动 joy_conventor
    ld.add_action(joy_conventor_launch)
    # 再启动 Fast-LIO
    # ld.add_action(fast_lio_node)
    ld.add_action(rviz_node)

    return ld
