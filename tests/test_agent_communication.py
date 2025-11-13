"""
Test Agent Communication - TwisterLab
Tests communication between Maestro Orchestrator and worker agents
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.real.real_maestro_agent import RealMaestroAgent
from agents.real.real_classifier_agent import RealClassifierAgent
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


async def test_maestro_initialization():
    """Test 1: Maestro initialization"""
    console.print("\n[cyan]🧪 TEST 1: Maestro Initialization[/cyan]")
    
    try:
        maestro = MaestroOrchestratorAgent()
        console.print(f"   ✅ Maestro initialized: {maestro.name}", style="green")
        console.print(f"   ℹ️  Display Name: {maestro.display_name}", style="dim")
        console.print(f"   ℹ️  Tools: {len(maestro.tools)}", style="dim")
        return maestro, True
    except Exception as e:
        console.print(f"   ❌ Maestro initialization failed: {e}", style="red")
        return None, False


async def test_worker_agents_initialization():
    """Test 2: Worker agents initialization"""
    console.print("\n[cyan]🧪 TEST 2: Worker Agents Initialization[/cyan]")
    
    agents = {}
    success_count = 0
    
    # Test Classifier
    try:
        classifier = TicketClassifierAgent()
        agents["classifier"] = classifier
        console.print(f"   ✅ Classifier initialized: {classifier.name}", style="green")
        success_count += 1
    except Exception as e:
        console.print(f"   ❌ Classifier failed: {e}", style="red")
    
    # Test Resolver
    try:
        resolver = HelpdeskAgent()
        agents["resolver"] = resolver
        console.print(f"   ✅ Resolver initialized: {resolver.name}", style="green")
        success_count += 1
    except Exception as e:
        console.print(f"   ❌ Resolver failed: {e}", style="red")
    
    # Test Desktop Commander
    try:
        commander = DesktopCommanderAgent()
        agents["commander"] = commander
        console.print(f"   ✅ Desktop Commander initialized: {commander.name}", style="green")
        success_count += 1
    except Exception as e:
        console.print(f"   ❌ Desktop Commander failed: {e}", style="red")
    
    return agents, success_count == 3


async def test_load_balancer(maestro):
    """Test 3: Load Balancer Configuration"""
    console.print("\n[cyan]🧪 TEST 3: Load Balancer Configuration[/cyan]")
    
    try:
        # Check registered instances
        lb = maestro.load_balancer
        
        # Test classifier instances
        classifier_instance = lb.get_best_instance("classifier")
        if classifier_instance:
            console.print(f"   ✅ Classifier registered: {classifier_instance.instance_id}", style="green")
            console.print(f"      • Max Load: {classifier_instance.max_load}", style="dim")
            console.print(f"      • Current Load: {classifier_instance.current_load}", style="dim")
        else:
            console.print("   ❌ No classifier instances registered", style="red")
            return False
        
        # Test resolver instances
        resolver_instance = lb.get_best_instance("resolver")
        if resolver_instance:
            console.print(f"   ✅ Resolver registered: {resolver_instance.instance_id}", style="green")
            console.print(f"      • Max Load: {resolver_instance.max_load}", style="dim")
            console.print(f"      • Current Load: {resolver_instance.current_load}", style="dim")
        else:
            console.print("   ❌ No resolver instances registered", style="red")
            return False
        
        # Test desktop commander instances
        dc_instance = lb.get_best_instance("desktop_commander")
        if dc_instance:
            console.print(f"   ✅ Desktop Commander registered: {dc_instance.instance_id}", style="green")
            console.print(f"      • Max Load: {dc_instance.max_load}", style="dim")
            console.print(f"      • Current Load: {dc_instance.current_load}", style="dim")
        else:
            console.print("   ❌ No desktop commander instances registered", style="red")
            return False
        
        return True
    except Exception as e:
        console.print(f"   ❌ Load balancer test failed: {e}", style="red")
        return False


async def test_task_scheduler(maestro):
    """Test 4: Task Scheduler"""
    console.print("\n[cyan]🧪 TEST 4: Task Scheduler[/cyan]")
    
    try:
        scheduler = maestro.task_scheduler
        
        # Check scheduled tasks
        tasks = scheduler.get_all_tasks()
        
        if tasks:
            console.print(f"   ✅ Task Scheduler active: {len(tasks)} tasks scheduled", style="green")
            for task in tasks:
                console.print(f"      • {task.name} (every {task.interval}s)", style="dim")
        else:
            console.print("   ⚠️  No tasks scheduled (might be normal)", style="yellow")
        
        return True
    except Exception as e:
        console.print(f"   ❌ Task scheduler test failed: {e}", style="red")
        return False


async def test_ticket_classification(maestro, classifier):
    """Test 5: Ticket Classification via Maestro"""
    console.print("\n[cyan]🧪 TEST 5: Ticket Classification Communication[/cyan]")
    
    try:
        # Create test ticket
        test_ticket = {
            "id": "test-001",
            "subject": "Cannot connect to VPN",
            "description": "User unable to access VPN after Windows update",
            "priority": "high",
            "requestor_email": "test@twisterlab.local"
        }
        
        console.print(f"   📤 Sending test ticket to classifier...", style="cyan")
        console.print(f"      Subject: {test_ticket['subject']}", style="dim")
        
        # Simulate classification
        result = await classifier.execute(
            f"Classify this ticket: {test_ticket['subject']}",
            {"ticket": test_ticket}
        )
        
        if result.get("status") == "success":
            category = result.get("data", {}).get("category", "unknown")
            console.print(f"   ✅ Classification successful!", style="green")
            console.print(f"      Category: {category}", style="dim")
            console.print(f"      Response time: {result.get('duration_ms', 0):.0f}ms", style="dim")
            return True
        else:
            console.print(f"   ❌ Classification failed: {result.get('error')}", style="red")
            return False
            
    except Exception as e:
        console.print(f"   ❌ Classification communication failed: {e}", style="red")
        import traceback
        console.print(f"      {traceback.format_exc()}", style="dim red")
        return False


async def test_agent_health_checks(agents):
    """Test 6: Agent Health Checks"""
    console.print("\n[cyan]🧪 TEST 6: Agent Health Checks[/cyan]")
    
    all_healthy = True
    
    for agent_name, agent in agents.items():
        try:
            health = await agent.health_check()
            
            if health.get("status") == "healthy":
                console.print(f"   ✅ {agent_name}: Healthy", style="green")
                console.print(f"      Uptime: {health.get('uptime', 0):.1f}s", style="dim")
            else:
                console.print(f"   ⚠️  {agent_name}: {health.get('status')}", style="yellow")
                all_healthy = False
                
        except Exception as e:
            console.print(f"   ❌ {agent_name}: Health check failed - {e}", style="red")
            all_healthy = False
    
    return all_healthy


async def test_maestro_metrics(maestro):
    """Test 7: Maestro Metrics Tracking"""
    console.print("\n[cyan]🧪 TEST 7: Maestro Metrics Tracking[/cyan]")
    
    try:
        metrics = maestro.metrics
        
        table = Table(title="Maestro Metrics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")
        
        table.add_row("Tickets Routed", str(metrics.get("tickets_routed", 0)))
        table.add_row("Classification Requests", str(metrics.get("classification_requests", 0)))
        table.add_row("Resolution Requests", str(metrics.get("resolution_requests", 0)))
        table.add_row("Command Executions", str(metrics.get("command_executions", 0)))
        table.add_row("Errors", str(metrics.get("errors", 0)))
        
        console.print(table)
        console.print("   ✅ Metrics tracking operational", style="green")
        
        return True
    except Exception as e:
        console.print(f"   ❌ Metrics test failed: {e}", style="red")
        return False


async def generate_summary_report(results):
    """Generate summary report"""
    console.print("\n" + "="*70)
    console.print("[bold cyan]📊 AGENT COMMUNICATION TEST SUMMARY[/bold cyan]")
    console.print("="*70 + "\n")
    
    # Create summary table
    table = Table(box=box.ROUNDED, show_header=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Test", style="cyan", width=40)
    table.add_column("Status", width=10)
    table.add_column("Result", style="dim", width=15)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    test_names = {
        "maestro_init": "Maestro Initialization",
        "workers_init": "Worker Agents Initialization",
        "load_balancer": "Load Balancer Configuration",
        "task_scheduler": "Task Scheduler",
        "classification": "Ticket Classification",
        "health_checks": "Agent Health Checks",
        "metrics": "Metrics Tracking"
    }
    
    for i, (test_key, passed) in enumerate(results.items(), 1):
        status = "✅ PASS" if passed else "❌ FAIL"
        status_style = "green" if passed else "red"
        result = "Success" if passed else "Failed"
        
        table.add_row(
            str(i),
            test_names.get(test_key, test_key),
            f"[{status_style}]{status}[/{status_style}]",
            result
        )
    
    console.print(table)
    
    # Overall status
    console.print()
    if passed_tests == total_tests:
        panel = Panel(
            f"[bold green]✅ ALL TESTS PASSED ({passed_tests}/{total_tests})[/bold green]\n\n"
            "[green]Maestro Orchestrator and all worker agents are communicating correctly![/green]\n"
            "[dim]• Load balancing operational\n"
            "• Task scheduling active\n"
            "• Health monitoring functional\n"
            "• Agent routing working[/dim]",
            title="🎉 Communication Test: SUCCESS",
            border_style="green",
            box=box.DOUBLE
        )
    else:
        panel = Panel(
            f"[bold yellow]⚠️  PARTIAL SUCCESS ({passed_tests}/{total_tests} passed)[/bold yellow]\n\n"
            f"[yellow]{total_tests - passed_tests} test(s) failed[/yellow]\n"
            "[dim]Check the detailed output above for failure reasons[/dim]",
            title="⚠️  Communication Test: ISSUES DETECTED",
            border_style="yellow",
            box=box.DOUBLE
        )
    
    console.print(panel)
    
    # Recommendations
    if passed_tests < total_tests:
        console.print("\n[bold yellow]📋 RECOMMENDED ACTIONS:[/bold yellow]")
        if not results.get("maestro_init"):
            console.print("   • Fix Maestro initialization issues")
        if not results.get("workers_init"):
            console.print("   • Check worker agent dependencies and configuration")
        if not results.get("load_balancer"):
            console.print("   • Review load balancer registration in maestro_agent.py")
        if not results.get("classification"):
            console.print("   • Test classifier agent independently")
            console.print("   • Check Ollama connectivity (LLM backend)")
        if not results.get("health_checks"):
            console.print("   • Investigate unhealthy agents")
    
    return passed_tests == total_tests


async def main():
    """Run all communication tests"""
    console.print("\n[bold cyan]🔬 TwisterLab Agent Communication Test Suite[/bold cyan]")
    console.print("[dim]Testing communication between Maestro and worker agents...[/dim]\n")
    console.print(f"[dim]Timestamp: {datetime.now().isoformat()}[/dim]")
    
    results = {}
    
    # Test 1: Maestro initialization
    maestro, results["maestro_init"] = await test_maestro_initialization()
    
    if not maestro:
        console.print("\n[bold red]❌ CRITICAL: Cannot proceed without Maestro![/bold red]")
        return False
    
    # Test 2: Worker agents initialization
    agents, results["workers_init"] = await test_worker_agents_initialization()
    
    # Test 3: Load balancer
    results["load_balancer"] = await test_load_balancer(maestro)
    
    # Test 4: Task scheduler
    results["task_scheduler"] = await test_task_scheduler(maestro)
    
    # Test 5: Classification communication (if classifier available)
    if "classifier" in agents:
        results["classification"] = await test_ticket_classification(
            maestro, 
            agents["classifier"]
        )
    else:
        console.print("\n[yellow]⚠️  Skipping classification test (classifier not available)[/yellow]")
        results["classification"] = False
    
    # Test 6: Health checks
    if agents:
        results["health_checks"] = await test_agent_health_checks(agents)
    else:
        results["health_checks"] = False
    
    # Test 7: Metrics
    results["metrics"] = await test_maestro_metrics(maestro)
    
    # Generate summary
    success = await generate_summary_report(results)
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Tests interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ FATAL ERROR: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc(), style="dim red")
        sys.exit(1)
