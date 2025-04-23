import os
from launch.actions import ExecuteProcess
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory, get_package_prefix

description_pkg = "hyperspawn_dropbear_description"
xacro_filename = "hyperspawn_dropbear.urdf.xacro"
def generate_launch_description():

    # Path to xacro file
    xacro_file = os.path.join(get_package_share_directory(description_pkg), 'urdf', xacro_filename)
    # model_arg
    model_args = DeclareLaunchArgument(
        name = "model",
        default_value = xacro_file,
        description = "Absolute path to robot urdf"
    )

    # Environment Variable
    os.environ["GAZEBO_MODEL_PATH"] = os.path.join(get_package_prefix(description_pkg), "share")

    # robot_description
    robot_description = ParameterValue(Command(
            ['xacro ', LaunchConfiguration("model")]
        )
    )

    # robot_state_publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}],
        arguments=[xacro_file],
    )
    
    start_gazebo_server_cmd = ExecuteProcess(
       cmd=[
            'gzserver',
            '-s',
            'libgazebo_ros_init.so',
            '-s',
            'libgazebo_ros_factory.so',
            "-u" # This ensures Gazebo starts paused
        ],        
        output='screen',
    )
    start_gazebo_client_cmd = ExecuteProcess(
        cmd=[
            'gzclient',
            '-s',
            'libgazebo_ros_init.so',
            '-s',
            'libgazebo_ros_factory.so',
        ],
        output='screen',)
    
    # Add delay for Gazebo to initialize
    from launch.actions import TimerAction
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "hyperspawn_dropbear_humanoid",
            "-topic", "/robot_description",
        ],
        output="screen"
    )

    delayed_spawn_entity = TimerAction(
        period=5.0,
        actions=[spawn_entity]
    )
    
    # gazebo spawn entity
    # spawn_entity = Node(
    #     package="gazebo_ros",
    #     executable="spawn_entity.py",
    #     arguments=["-entity", "hyperspawn_dropbear_humanoid", "-topic", "robot_description"],
    #     output="screen",
    # )

    return LaunchDescription([
        model_args,
        robot_state_publisher,
        start_gazebo_server_cmd,
        start_gazebo_client_cmd,
        delayed_spawn_entity,
        # spawn_entity,
    ])


# import os
# from launch import LaunchDescription
# from launch.actions import ExecuteProcess, DeclareLaunchArgument
# from launch.substitutions import Command, LaunchConfiguration
# from launch_ros.actions import Node
# from launch_ros.parameter_descriptions import ParameterValue
# from ament_index_python.packages import get_package_share_directory

# description_pkg = "hyperspawn_dropbear_description"
# xacro_filename = "hyperspawn_dropbear.urdf.xacro"

# def generate_launch_description():
#     # Path to xacro file
#     xacro_file = os.path.join(get_package_share_directory(description_pkg), 'urdf', xacro_filename)
    
#     model_arg = DeclareLaunchArgument(
#         name="model",
#         default_value=xacro_file,
#         description="Absolute path to robot urdf"
#     )

#     # Set GAZEBO_MODEL_PATH
#     # os.environ["GAZEBO_MODEL_PATH"] = os.path.join(
#     #     get_package_share_directory(description_pkg),
#     #     "share"
#     # )

#     robot_description = ParameterValue(
#         Command(['xacro ', LaunchConfiguration("model")]),
#         value_type=str
#     )

#     robot_state_publisher = Node(
#         package="robot_state_publisher",
#         executable="robot_state_publisher",
#         parameters=[{"robot_description": robot_description}],
#         output="screen"
#     )

#     # Start Gazebo with ROS integration
#     gazebo_server = ExecuteProcess(
#         cmd=['gzserver', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so'],
#         output='screen'
#     )

#     gazebo_client = ExecuteProcess(
#         cmd=['gzclient'],
#         output='screen'
#     )

#     # Add delay for Gazebo to initialize
#     from launch.actions import TimerAction
#     spawn_entity = Node(
#         package="gazebo_ros",
#         executable="spawn_entity.py",
#         arguments=[
#             "-entity", "hyperspawn_dropbear_humanoid",
#             "-topic", "/robot_description",
#         ],
#         output="screen"
#     )

#     delayed_spawn_entity = TimerAction(
#         period=5.0,
#         actions=[spawn_entity]
#     )

#     return LaunchDescription([
#         model_arg,
#         robot_state_publisher,
#         gazebo_server,
#         gazebo_client,
#         delayed_spawn_entity,
#     ])