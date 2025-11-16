"""
TwisterLab v1.0.0 - Final Load Testing
Tests system under 1000+ concurrent ticket load to validate production readiness.

Target Metrics:
- Throughput: >100 tickets/sec
- Latency p95: <500ms
- Latency p99: <1s
- Error rate: <1%
- Resource usage: CPU <80%, Memory <80%
"""

import asyncio
import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
import psutil


@dataclass
class LoadTestResult:
    """Results from load test execution"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    duration_seconds: float
    throughput_per_sec: float
    latencies_ms: List[float]
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_latency_ms: float
    error_rate_percent: float
    avg_cpu_percent: float
    avg_memory_percent: float
    errors: Dict[str, int]


class LoadTester:
    """Load testing framework for TwisterLab API"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.latencies: List[float] = []
        self.errors: Dict[str, int] = {}
        self.successful = 0
        self.failed = 0
        self.cpu_samples: List[float] = []
        self.memory_samples: List[float] = []

    async def create_ticket(self, session: aiohttp.ClientSession, ticket_id: int) -> Dict[str, Any]:
        """
        Create a single ticket via API.

        Args:
            session: aiohttp session
            ticket_id: Unique ticket identifier

        Returns:
            Result dict with status and timing
        """
        ticket_data = {
            "subject": f"Load Test Ticket #{ticket_id}",
            "description": f"Automated load test ticket - {datetime.now().isoformat()}",
            "priority": "medium",
            "source": "load_test",
        }

        start_time = time.time()

        try:
            async with session.post(
                f"{self.base_url}/api/v1/tickets",
                json=ticket_data,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                elapsed_ms = (time.time() - start_time) * 1000

                if response.status in [200, 201]:
                    self.successful += 1
                    self.latencies.append(elapsed_ms)
                    data = await response.json()
                    return {
                        "status": "success",
                        "latency_ms": elapsed_ms,
                        "ticket_id": data.get("id"),
                    }
                else:
                    self.failed += 1
                    error_key = f"http_{response.status}"
                    self.errors[error_key] = self.errors.get(error_key, 0) + 1
                    return {
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                        "latency_ms": elapsed_ms,
                    }

        except asyncio.TimeoutError:
            elapsed_ms = (time.time() - start_time) * 1000
            self.failed += 1
            self.errors["timeout"] = self.errors.get("timeout", 0) + 1
            return {"status": "failed", "error": "timeout", "latency_ms": elapsed_ms}

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.failed += 1
            error_key = type(e).__name__
            self.errors[error_key] = self.errors.get(error_key, 0) + 1
            return {"status": "failed", "error": str(e), "latency_ms": elapsed_ms}

    def sample_system_resources(self):
        """Sample CPU and memory usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent

            self.cpu_samples.append(cpu_percent)
            self.memory_samples.append(memory_percent)
        except Exception as e:
            print(f"Warning: Could not sample resources: {e}")

    async def run_load_test(
        self, num_requests: int = 1000, concurrency: int = 50
    ) -> LoadTestResult:
        """
        Execute load test with specified concurrency.

        Args:
            num_requests: Total number of requests to send
            concurrency: Number of concurrent requests

        Returns:
            LoadTestResult with all metrics
        """
        print(f"\n{'='*60}")
        print(f"  TwisterLab Load Test - {num_requests} requests @ {concurrency} concurrent")
        print(f"{'='*60}\n")

        # Reset counters
        self.latencies = []
        self.errors = {}
        self.successful = 0
        self.failed = 0
        self.cpu_samples = []
        self.memory_samples = []

        # Create session with connection pooling
        connector = aiohttp.TCPConnector(limit=concurrency)
        timeout = aiohttp.ClientTimeout(total=30)

        start_time = time.time()

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create batches of concurrent requests
            tasks = []
            for i in range(num_requests):
                task = self.create_ticket(session, i)
                tasks.append(task)

                # Execute in batches to maintain concurrency limit
                if len(tasks) >= concurrency:
                    # Sample resources while executing
                    self.sample_system_resources()
                    await asyncio.gather(*tasks)
                    tasks = []

            # Execute remaining tasks
            if tasks:
                self.sample_system_resources()
                await asyncio.gather(*tasks)

        duration = time.time() - start_time

        # Calculate metrics
        total_requests = self.successful + self.failed
        throughput = total_requests / duration if duration > 0 else 0
        error_rate = (self.failed / total_requests * 100) if total_requests > 0 else 0

        # Latency percentiles
        if self.latencies:
            self.latencies.sort()
            p50 = statistics.median(self.latencies)
            p95 = self.latencies[int(len(self.latencies) * 0.95)]
            p99 = self.latencies[int(len(self.latencies) * 0.99)]
            avg = statistics.mean(self.latencies)
        else:
            p50 = p95 = p99 = avg = 0

        # Resource usage
        avg_cpu = statistics.mean(self.cpu_samples) if self.cpu_samples else 0
        avg_memory = statistics.mean(self.memory_samples) if self.memory_samples else 0

        result = LoadTestResult(
            total_requests=total_requests,
            successful_requests=self.successful,
            failed_requests=self.failed,
            duration_seconds=duration,
            throughput_per_sec=throughput,
            latencies_ms=self.latencies,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            avg_latency_ms=avg,
            error_rate_percent=error_rate,
            avg_cpu_percent=avg_cpu,
            avg_memory_percent=avg_memory,
            errors=self.errors,
        )

        return result

    def print_results(self, result: LoadTestResult):
        """Print formatted test results"""
        print(f"\n{'='*60}")
        print(f"  LOAD TEST RESULTS")
        print(f"{'='*60}\n")

        # Summary
        print(f"Total Requests:      {result.total_requests}")
        print(
            f"Successful:          {result.successful_requests} ({result.successful_requests/result.total_requests*100:.1f}%)"
        )
        print(f"Failed:              {result.failed_requests} ({result.error_rate_percent:.2f}%)")
        print(f"Duration:            {result.duration_seconds:.2f}s")
        print(f"Throughput:          {result.throughput_per_sec:.2f} requests/sec")

        # Latency
        print(f"\nLatency Metrics:")
        print(f"  Average:           {result.avg_latency_ms:.2f}ms")
        print(f"  p50 (median):      {result.p50_latency_ms:.2f}ms")
        print(f"  p95:               {result.p95_latency_ms:.2f}ms")
        print(f"  p99:               {result.p99_latency_ms:.2f}ms")

        # Resource usage
        print(f"\nResource Usage:")
        print(f"  CPU (avg):         {result.avg_cpu_percent:.1f}%")
        print(f"  Memory (avg):      {result.avg_memory_percent:.1f}%")

        # Errors
        if result.errors:
            print(f"\nErrors Breakdown:")
            for error_type, count in sorted(
                result.errors.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  {error_type}: {count}")

        # Pass/Fail assessment
        print(f"\n{'='*60}")
        print(f"  ASSESSMENT")
        print(f"{'='*60}\n")

        checks = [
            (
                "Throughput",
                result.throughput_per_sec >= 100,
                f"{result.throughput_per_sec:.1f} >= 100 req/s",
            ),
            ("p95 Latency", result.p95_latency_ms < 500, f"{result.p95_latency_ms:.1f}ms < 500ms"),
            (
                "p99 Latency",
                result.p99_latency_ms < 1000,
                f"{result.p99_latency_ms:.1f}ms < 1000ms",
            ),
            (
                "Error Rate",
                result.error_rate_percent < 1.0,
                f"{result.error_rate_percent:.2f}% < 1%",
            ),
            ("CPU Usage", result.avg_cpu_percent < 80, f"{result.avg_cpu_percent:.1f}% < 80%"),
            (
                "Memory Usage",
                result.avg_memory_percent < 80,
                f"{result.avg_memory_percent:.1f}% < 80%",
            ),
        ]

        all_passed = True
        for check_name, passed, details in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}  {check_name:15s}  {details}")
            all_passed = all_passed and passed

        print(f"\n{'='*60}")
        if all_passed:
            print("  🎉 ALL CHECKS PASSED - PRODUCTION READY")
        else:
            print("  ⚠️  SOME CHECKS FAILED - REVIEW REQUIRED")
        print(f"{'='*60}\n")

    def save_results(self, result: LoadTestResult, filename: str = "load_test_results.json"):
        """Save results to JSON file"""
        # Convert to dict, excluding latencies list (too large)
        result_dict = asdict(result)
        result_dict["latencies_ms"] = f"[{len(result.latencies_ms)} samples]"

        with open(filename, "w") as f:
            json.dump(result_dict, f, indent=2)

        print(f"Results saved to: {filename}")


async def main():
    """Execute load test scenarios"""
    tester = LoadTester(base_url="http://localhost:8001")

    print("\n🚀 TwisterLab v1.0.0 - Final Load Testing")
    print(f"Target: http://localhost:8001")
    print(f"Time: {datetime.now().isoformat()}\n")

    # Wait for user confirmation
    input("Press ENTER to start load test (ensure staging environment is running)...")

    # Test 1: Warm-up (100 requests, 10 concurrent)
    print("\n📊 Test 1: Warm-up")
    result_warmup = await tester.run_load_test(num_requests=100, concurrency=10)
    tester.print_results(result_warmup)

    await asyncio.sleep(5)  # Cool-down

    # Test 2: Moderate load (500 requests, 25 concurrent)
    print("\n📊 Test 2: Moderate Load")
    result_moderate = await tester.run_load_test(num_requests=500, concurrency=25)
    tester.print_results(result_moderate)
    tester.save_results(result_moderate, "load_test_moderate.json")

    await asyncio.sleep(10)  # Cool-down

    # Test 3: Heavy load (1000 requests, 50 concurrent)
    print("\n📊 Test 3: Heavy Load")
    result_heavy = await tester.run_load_test(num_requests=1000, concurrency=50)
    tester.print_results(result_heavy)
    tester.save_results(result_heavy, "load_test_heavy.json")

    await asyncio.sleep(10)  # Cool-down

    # Test 4: Extreme load (2000 requests, 100 concurrent)
    print("\n📊 Test 4: Extreme Load (Stress Test)")
    result_extreme = await tester.run_load_test(num_requests=2000, concurrency=100)
    tester.print_results(result_extreme)
    tester.save_results(result_extreme, "load_test_extreme.json")

    print("\n✅ Load testing complete!")
    print(f"Check Grafana dashboards for real-time metrics: http://localhost:3001")


if __name__ == "__main__":
    asyncio.run(main())
