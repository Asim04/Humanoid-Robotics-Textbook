/*
 * File: gazebo_world_plugin.cpp
 * Purpose: Example Gazebo world plugin for custom physics or environment effects
 * Chapter: 6 - Gazebo Classic & Fortress
 * Dependencies: gazebo, physics libraries
 * Hardware: Simulation environment
 */

#include <gazebo/common/Plugin.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/gazebo.hh>

#include <iostream>
#include <vector>

namespace gazebo
{
  class WindFieldPlugin : public WorldPlugin
  {
    public:
      // Constructor
      void Load(physics::WorldPtr _world, sdf::ElementPtr _sdf)
      {
        // Store the world pointer
        this->world = _world;

        // Get parameters from SDF
        if (_sdf->HasElement("windForce"))
          this->windForce = _sdf->Get<math::Vector3>("windForce");
        else
          this->windForce = math::Vector3(0.5, 0.0, 0.0); // Default wind

        if (_sdf->HasElement("windVariance"))
          this->windVariance = _sdf->Get<double>("windVariance");
        else
          this->windVariance = 0.1; // Default variance

        // Connect to the world update event
        this->updateConnection = event::Events::ConnectWorldUpdateBegin(
            std::bind(&WindFieldPlugin::OnUpdate, this));

        std::cout << "WindFieldPlugin loaded with force: "
                  << this->windForce << std::endl;
      }

    public:
      // Called on every world update
      void OnUpdate()
      {
        // Get all models in the world
        physics::Model_V models = this->world->GetModels();

        // Apply wind force to each model
        for (auto model : models)
        {
          // Only apply to dynamic models (not static ground plane)
          if (model->IsStatic())
            continue;

          // Calculate variable wind force based on position and time
          double time = this->world->GetSimTime().Double();
          math::Vector3 variableWind = this->windForce;

          // Add some spatial and temporal variation
          math::Pose modelPose = model->GetWorldPose();
          variableWind.x += this->windVariance *
            sin(time + modelPose.pos.x * 0.1) * cos(time * 2);
          variableWind.y += this->windVariance *
            cos(time * 1.5 + modelPose.pos.y * 0.1) * sin(time);
          variableWind.z += this->windVariance * sin(time * 0.7);

          // Apply force to the model's center of mass
          math::Vector3 forcePoint = model->GetWorldPose().pos;
          model->GetLink()->AddForceAtWorldPosition(variableWind, forcePoint);
        }
      }

    private:
      // Pointer to the world
      physics::WorldPtr world;

      // Wind parameters
      math::Vector3 windForce;
      double windVariance;

      // Update event connection
      event::ConnectionPtr updateConnection;
  };

  // Register this plugin with the simulator
  GZ_REGISTER_WORLD_PLUGIN(WindFieldPlugin)
}