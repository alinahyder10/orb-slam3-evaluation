import numpy as np
import matplotlib.pyplot as plt

# Load data: timestamp, x, y, z, qx, qy, qz, qw
try:
    data = np.loadtxt('KeyFrameTrajectory.txt')
    x, y, z = data[:, 1], data[:, 2], data[:, 3]

    # Create a 3D plot
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(projection='3d')
    ax.plot(x, y, z, color='blue', linewidth=2, label='Camera Trajectory')
    
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters)')
    plt.title('ORB-SLAM3 Estimated Camera Path')
    plt.legend()
    
    # Save the output image
    plt.savefig('trajectory.png', dpi=300)
    print("Success! Plot saved as 'trajectory.png'")
except Exception as e:
    print(f"Error reading file: {e}")
