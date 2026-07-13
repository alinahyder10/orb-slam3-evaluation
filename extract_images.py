import os
from pathlib import Path
import cv2
import numpy as np
from rosbags.highlevel import AnyReader

bag_path = "Datasets/MH01/Low-Feature Environment/bonirob_2016-04-27-13-05-33_0.bag"
output_dir = Path("Datasets/MH01/Low-Feature Environment")

# Create target directories
cam0_dir = output_dir / "cam0" / "data"
cam1_dir = output_dir / "cam1" / "data"
cam0_dir.mkdir(parents=True, exist_ok=True)
cam1_dir.mkdir(parents=True, exist_ok=True)

print("Extracting JAI RGB and NIR images from bag file...")

with AnyReader([Path(bag_path)]) as reader:
    # Explicitly map the multi-spectral topics to cam0 and cam1
    topic_mapping = {
        "/camera/jai/rgb/image": cam0_dir,
        "/camera/jai/nir/image": cam1_dir
    }
    
    connections = [x for x in reader.connections if x.topic in topic_mapping]
    count = 0
    
    for connection, timestamp, rawdata in reader.messages(connections=connections):
        msg = reader.deserialize(rawdata, connection.msgtype)
        
        if hasattr(msg, 'data'):
            np_arr = np.frombuffer(msg.data, dtype=np.uint8)
            
            # Calculate channels based on data size vs dimensions
            channels = len(msg.data) // (msg.height * msg.width)
            
            if channels == 3:
                img = np_arr.reshape((msg.height, msg.width, 3))
            else:
                img = np_arr.reshape((msg.height, msg.width))
                
            # Save to correct folder using timestamp as filename
            time_str = f"{timestamp}"
            target_path = topic_mapping[connection.topic] / f"{time_str}.png"
            cv2.imwrite(str(target_path), img)
            count += 1

print(f"Extraction complete! Successfully saved {count} images to Datasets/MH01/Low-Feature Environment.")