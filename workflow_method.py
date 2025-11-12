    async def process_ticket_workflow(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a ticket through the complete workflow:
        1. ClassifierAgent analyzes and routes
        2. ResolverAgent executes SOP if routed there
        3. DesktopCommanderAgent runs commands if routed there

        Args:
            ticket: Ticket data with title, description, etc

        Returns:
            Complete workflow results with all steps
        """
        logger.info(f"🎫 Processing ticket workflow: {ticket.get('ticket_id', 'Unknown')}")

        workflow_results = {
            "ticket_id": ticket.get("ticket_id"),
            "start_time": datetime.now().isoformat(),
            "steps": []
        }

        try:
            # Step 1: Classify ticket
            logger.info("📋 Step 1/3: Classifying ticket...")
            classifier = self.agents.get("classifier")
            if not classifier:
                raise ValueError("ClassifierAgent not initialized")

            classification_result = await classifier.execute({
                "operation": "classify_ticket",
                "ticket": ticket
            })

            workflow_results["steps"].append({
                "step": "classification",
                "agent": "ClassifierAgent",
                "result": classification_result,
                "timestamp": datetime.now().isoformat()
            })

            if classification_result.get("status") != "success":
                raise ValueError(f"Classification failed: {classification_result.get('error')}")

            classification = classification_result.get("classification", {})
            routed_to = classification.get("routed_to_agent", "ResolverAgent")
            category = classification.get("category", "general")

            logger.info(f"✅ Classified as '{category}', routing to {routed_to}")

            # Step 2: Execute resolver if routed there
            if routed_to == "ResolverAgent":
                logger.info("🔧 Step 2/3: Executing ResolverAgent with SOP...")
                resolver = self.agents.get("resolver")
                if resolver:
                    # Map category to SOP
                    sop_map = {
                        "network": "network_troubleshoot",
                        "software": "software_install",
                        "performance": "disk_cleanup",
                        "security": "password_reset",
                        "database": "database_optimization",
                        "system": "service_restart"
                    }
                    sop_id = sop_map.get(category, "network_troubleshoot")

                    resolver_result = await resolver.execute({
                        "operation": "execute_sop",
                        "sop_id": sop_id,
                        "ticket": ticket
                    })

                    workflow_results["steps"].append({
                        "step": "resolution",
                        "agent": "ResolverAgent",
                        "sop_executed": sop_id,
                        "result": resolver_result,
                        "timestamp": datetime.now().isoformat()
                    })

                    logger.info(f"✅ ResolverAgent completed SOP: {sop_id}")
                else:
                    logger.warning("⚠️ ResolverAgent not available")

            # Step 3: Execute DesktopCommander if routed there
            elif routed_to == "DesktopCommanderAgent":
                logger.info("💻 Step 2/3: Executing DesktopCommanderAgent...")
                commander = self.agents.get("desktop_commander")
                if commander:
                    # Map category to diagnostic command
                    command_map = {
                        "network": "ping 8.8.8.8 -c 4",
                        "hardware": "df -h && free -h",
                        "performance": "top -b -n 1 | head -20"
                    }
                    command = command_map.get(category, "echo 'Diagnostic: No specific command for this category'")

                    commander_result = await commander.execute({
                        "operation": "execute_command",
                        "command": command,
                        "ticket": ticket
                    })

                    workflow_results["steps"].append({
                        "step": "command_execution",
                        "agent": "DesktopCommanderAgent",
                        "command": command,
                        "result": commander_result,
                        "timestamp": datetime.now().isoformat()
                    })

                    logger.info(f"✅ DesktopCommanderAgent executed command")
                else:
                    logger.warning("⚠️ DesktopCommanderAgent not available")

            # Step 3: Other agents (MonitoringAgent, SyncAgent)
            else:
                logger.info(f"📊 Step 2/3: Routing to {routed_to}...")
                agent = self.agents.get(routed_to.lower().replace("agent", ""))
                if agent:
                    agent_result = await agent.execute({
                        "operation": "health_check",
                        "ticket": ticket
                    })

                    workflow_results["steps"].append({
                        "step": "agent_execution",
                        "agent": routed_to,
                        "result": agent_result,
                        "timestamp": datetime.now().isoformat()
                    })

                    logger.info(f"✅ {routed_to} completed")

            workflow_results["status"] = "success"
            workflow_results["end_time"] = datetime.now().isoformat()
            workflow_results["summary"] = f"Ticket processed: {category} -> {routed_to}"

            logger.info(f"🎉 Ticket workflow completed successfully!")
            return workflow_results

        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            workflow_results["status"] = "error"
            workflow_results["error"] = str(e)
            workflow_results["end_time"] = datetime.now().isoformat()
            return workflow_results
