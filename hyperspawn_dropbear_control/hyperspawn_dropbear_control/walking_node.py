#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Float64MultiArray

class GaitManager:
    def __init__(self):
        self.phases = {
            'right_swing': {
                'right_leg': {
                    'hip': -0.594, 
                    'knee': -0.325, 
                    'lower_leg': 0.0,
                    'foot': 0.0
                },
                'left_leg': {
                    'hip': 0.334, 
                    'knee': 0.0, 
                    'lower_leg': 0.0,
                    'foot': 0.0
                },
                'right_arm': {
                    'yaw': 0.5,
                    'pitch': 0.0,
                    'roll': 0.0,
                    'wrist': 0.0,
                    'elbow': 2.0
                },
                'left_arm': {
                    'yaw': 0.5,
                    'pitch': 0.0,
                    'roll': 0.0,
                    'wrist': 0.0,
                    'elbow': -0.50
                }
            },
            'left_swing': {
                'right_leg': {
                    'hip': 0.334, 
                    'knee': 0.0, 
                    'lower_leg': 0.0,
                    'foot': 0.0
                },
                'left_leg': {
                    'hip': -0.594, 
                    'knee': -0.325, 
                    'lower_leg': 0.0,
                    'foot': 0.0
                },
                'right_arm': {
                    'yaw': -0.5,
                    'pitch': 0.0,
                    'roll': 0.0,
                    'wrist': 0.0,
                    'elbow': 0.5
                },
                'left_arm': {
                    'yaw': -0.5,
                    'pitch': 0.0,
                    'roll': 0.0,
                    'wrist': 0.0,
                    'elbow': -2.0
                }
            }
        }
        self.current_phase = 'left_swing'
        self.phase_progress = 0  # 0-100
        self.phase_duration = 0.9  # seconds
        
    def update(self):
        self.current_phase = 'left_swing' if self.current_phase == 'right_swing' else 'right_swing'
        return self.phases[self.current_phase], self.current_phase

class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')
        self.gait = GaitManager()
        self.target_pose, phase_ = self.gait.update()

        # Initialize all joints exactly as specified
        self.init_joints()
        self.init_publishers()

        # Control frequencies
        self.high_freq = 60.0  # Hz (effort controllers)
        self.low_freq = 1.0    # Hz (trajectory controllers)
        
        # Single timer that runs at the higher frequency (60Hz)
        self.timer = self.create_timer(1.0 / self.high_freq, self.combined_callback)
        
        # Counter to manage different rates
        self.high_freq_counter = 0

    def init_joints(self):
        # Leg joints 
        self.leg_joints = {
            'right': {
                'hip': ['RL_hip_joint'],
                'knee': ['RL_knee_actuator_joint'],
                'lower_leg': ['RL_Revolute67'],
                'foot': ['RL_Revolute87']
            },
            'left': {
                'hip': ['LL_hip_joint'],
                'knee': ['LL_knee_actuator_joint'],
                'lower_leg': ['LL_Revolute67'],
                'foot': ['LL_Revolute87']
            }
        }
        
        # Arm joints 
        self.arm_joints = {
            'right': {
                'hand': ['RH_yaw', 'RH_pitch', 'RH_roll', 'RH_wrist_roll'],
                'elbow': ['RH_elbow_joint']
            },
            'left': {
                'hand': ['LH_yaw', 'LH_pitch', 'LH_roll', 'LH_wrist_roll'],
                'elbow': ['LH_elbow_joint']
            }
        }

    def init_publishers(self):
        self.publishers_ = {
            # Leg publishers
            'right_leg_hip': self.create_publisher(JointTrajectory, '/right_leg_hip_joint_controller/joint_trajectory', 10),
            'left_leg_hip': self.create_publisher(JointTrajectory, '/left_leg_hip_joint_controller/joint_trajectory', 10),
            'right_leg_foot': self.create_publisher(JointTrajectory, '/right_leg_foot_controller/joint_trajectory', 10),
            'left_leg_foot': self.create_publisher(JointTrajectory, '/left_leg_foot_controller/joint_trajectory', 10),
            'right_leg_knee': self.create_publisher(Float64MultiArray, '/right_leg_knee_controller/commands', 10),
            'left_leg_knee': self.create_publisher(Float64MultiArray, '/left_leg_knee_controller/commands', 10),
            'right_leg_lower': self.create_publisher(Float64MultiArray, '/lower_right_leg_controller/commands', 10),
            'left_leg_lower': self.create_publisher(Float64MultiArray, '/lower_left_leg_controller/commands', 10),
            
            # Arm publishers 
            'right_hand': self.create_publisher(JointTrajectory, '/right_hand_controller/joint_trajectory', 10),
            'left_hand': self.create_publisher(JointTrajectory, '/left_hand_controller/joint_trajectory', 10),
            'right_elbow': self.create_publisher(Float64MultiArray, '/right_hand_elbow_controller/commands', 10),
            'left_elbow': self.create_publisher(Float64MultiArray, '/left_hand_elbow_controller/commands', 10)
        }

    def combined_callback(self):
        """Combined callback that handles both controllers at different rates."""
        # Always run the high frequency (60Hz) effort controllers
        self.control_efforts(self.target_pose)
        
        # Only run the trajectory controllers at 1Hz
        self.high_freq_counter += 1
        if self.high_freq_counter >= (self.high_freq / self.low_freq):
            self.high_freq_counter = 0
            self.control_trajectories(self.target_pose)
            self.target_pose, phase_ = self.gait.update()
            self.get_logger().info(f"Current phase: {phase_}")

    def control_trajectories(self, target_pose):
        """Control all trajectory-based joints (1Hz)."""
        # Legs
        for side in ['right', 'left']:
            # Hip trajectory
            self.publish_trajectory(
                f'{side}_leg_hip',
                self.leg_joints[side]['hip'],
                [target_pose[f'{side}_leg']['hip']],
                self.gait.phase_duration
            )
            
            # Foot trajectory
            self.publish_trajectory(
                f'{side}_leg_foot',
                self.leg_joints[side]['foot'],
                [target_pose[f'{side}_leg']['foot']],
                self.gait.phase_duration
            )
        
        # Arms
        for side in ['right', 'left']:
            # Hand trajectory
            hand_joints = self.arm_joints[side]['hand']
            hand_positions = [
                target_pose[f'{side}_arm']['yaw'],
                target_pose[f'{side}_arm']['pitch'],
                target_pose[f'{side}_arm']['roll'],
                target_pose[f'{side}_arm']['wrist']
            ]
            self.publish_trajectory(
                f'{side}_hand',
                hand_joints,
                hand_positions,
                self.gait.phase_duration
            )

    def control_efforts(self, target_pose):
        """Control all effort-based joints (60Hz)."""
        # Legs
        for side in ['right', 'left']:
            # Knee effort
            self.publish_effort(
                f'{side}_leg_knee',
                self.leg_joints[side]['knee'],
                [target_pose[f'{side}_leg']['knee']]
            )
            
            # Lower leg effort
            self.publish_effort(
                f'{side}_leg_lower',
                self.leg_joints[side]['lower_leg'],
                [target_pose[f'{side}_leg']['lower_leg']]
            )
        
        # Arms
        for side in ['right', 'left']:
            # Elbow effort
            self.publish_effort(
                f'{side}_elbow',
                self.arm_joints[side]['elbow'],
                [target_pose[f'{side}_arm']['elbow']]
            )

    def publish_trajectory(self, controller, joint_names, positions, duration):
        trajectory = JointTrajectory()
        trajectory.joint_names = joint_names
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = rclpy.duration.Duration(seconds=duration).to_msg()
        trajectory.points.append(point)
        self.publishers_[controller].publish(trajectory)

    def publish_effort(self, controller, joint_names, efforts):
        msg = Float64MultiArray()
        msg.data = efforts
        self.publishers_[controller].publish(msg)

def main(args=None):
    rclpy.init(args=args)
    controller = HumanoidController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()