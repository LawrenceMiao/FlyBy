# FlyBy
> By Lawrence Miao, Miranda Zheng, and Raymond Chen

A project for the February 2025 NSBE-SHPE Climate Change & Sustainability Hackathon @ Rensselaer Polytechnic Institute.
 
FlyBy is an AI-powered web application that leverages a [YOLOv5](https://github.com/ultralytics/yolov5) vision model and the [TACO dataset](https://github.com/pedropro/TACO) to detect and classify trash easily and effectively.
## How does it work?
1. On the website, upload a video of drone footage to analyze for trash.
2. The system will analyze the video in no more than a few minutes.
3. The video is played back to you with bounding boxes and classifications drawn on top of all instances of detected trash!
4. You will also see metrics including:
    - Total number of detected items.
    - A breakdown detailing the number of each item type detected.
## Project Issue
Every year, 19 - 23 MILLION tons of plastic waste are dumped into our oceans. This in turn leaks into aquatic ecosystems, polluting lakes, rivers and seas. It's polluting habitats, contributing to the already high level of methane emissions, and affecting the livelihood of all animals.

We're proud to present FlyBy: our 24-hour solution to mitiagting this long-standing problem!

The system integrates with a drone-mounted camera to analyze remote environments such as oceans, forests, and other inaccessible areas where manual waste monitoring is challenging.
## Use Cases
- Ocean Cleanup
- Forest and Wildlife Conservation
- Smart Cities and Waste Management
- Disaster Relief and Emergency Response
## Target Audiences
- Environmental Conservation Groups
- Municipal Government Waste Management Departments
- Marine and Wildlife Protection Agencies
- Drone Communities
## Our Technology Stack
**Front-end:** React with TypeScript and TailwindCSS. \
**Back-end:** Python with FastAPI and PyTorch. \
**Model:** YOLOv5 trained on the TACO dataset.