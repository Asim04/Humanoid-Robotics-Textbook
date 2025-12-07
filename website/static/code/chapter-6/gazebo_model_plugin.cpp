/*
 * File: gazebo_model_plugin.cpp
 * Purpose: Example Gazebo model plugin for robotics simulation
 * Chapter: 6 - Gazebo Classic & Fortress
 * Dependencies: gazebo, ROS 2
 * Hardware: Simulated robot in Gazebo
 */

#include <gazebo/common/Plugin.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/transport/transport.hh>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/gazebo.hh>

#include <iostream>
#include <string>

namespace gazebo
{
  class RobotMotionPlugin : public ModelPlugin
  {
    public:
      // Constructor
      void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf)
      {
        // Store the model pointer for later use
        this->model = _model;

        // Get parameters from SDF if they exist
        if (_sdf->HasElement("robotSpeed"))
          this->speed = _sdf->Get<double>("robotSpeed");
        else
          this->speed = 0.5; // Default speed

        // Initialize the velocity to zero
        this->targetVel = 0;

        // Listen to the update event. This event is broadcast every
        // simulation iteration.
        this->updateConnection = event::Events::ConnectWorldUpdateBegin(
            std::bind(&RobotMotionPlugin::OnUpdate, this));

        std::cout << "RobotMotionPlugin loaded for model: "
                  << _model->GetName() << std::endl;
      }

    public:
      // Called by the world update start event
      void OnUpdate()
      {
        // Apply velocity to the first (and only) child link
        if (this->model->GetChildCount() > 0)
        {
          // Get the first link
          physics::LinkPtr link = this->model->GetLink();

          // Set the linear velocity
          math::Vector3 vel = math::Vector3(this->targetVel, 0, 0);
          link->SetLinearVel(vel);

          // Add some rotation around the Z axis
          math::Vector3 rot = math::Vector3(0, 0, 0.2);
          link->SetAngularVel(rot);
        }
      }

    private:
      // Pointer to the model
      physics::ModelPtr model;

      // Pointer to the update event connection
      event::ConnectionPtr updateConnection;

      // Target velocity for the robot
      double targetVel;

      // Speed parameter
      double speed;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_MODEL_PLUGIN(RobotMotionPlugin)
}