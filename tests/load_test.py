"""
Load Testing Script
Tests system performance under load
"""

import os
import sys
import time
import asyncio
import statistics
import concurrent.futures
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from orchestration import GiftRecommendationOrchestrator, RecommendationRequest

@dataclass
class LoadTestResult:
    """Results from load testing"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    errors: List[str]

class LoadTester:
    """Load testing utility for GiftPedia"""
    
    def __init__(self):
        self.orchestrator = GiftRecommendationOrchestrator()
        self.test_requests = self._generate_test_requests()
    
    def _generate_test_requests(self) -> List[str]:
        """Generate diverse test requests"""
        return [
            "I need a birthday gift for my brother who is 28 years old, loves music and guitar, budget is ₹2000",
            "Looking for anniversary gift for my wife who enjoys cooking and gardening, budget ₹3000",
            "Graduation gift for daughter who loves reading and writing, budget ₹1500",
            "Father's Day gift for dad who is into technology and gadgets, budget ₹5000",
            "Wedding gift for best friend who loves travel and photography, budget ₹4000",
            "Baby shower gift for sister expecting first child, budget ₹2500",
            "Housewarming gift for couple moving into new apartment, budget ₹2000",
            "Retirement gift for boss who loves golf, budget ₹3000",
            "Valentine's Day gift for girlfriend who loves fashion and makeup, budget ₹2500",
            "Christmas gift for mom who enjoys knitting and crafts, budget ₹1500"
        ]
    
    def single_request_test(self, user_input: str) -> Dict[str, Any]:
        """Test a single request and return metrics"""
        start_time = time.time()
        
        try:
            request = RecommendationRequest(
                user_input=user_input,
                max_recommendations=3
            )
            
            response = self.orchestrator.get_recommendations(request)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': True,
                'response_time': response_time,
                'num_recommendations': len(response.recommendations),
                'processing_time': response.processing_time,
                'session_id': response.session_id
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': False,
                'response_time': response_time,
                'error': str(e)
            }
    
    def concurrent_load_test(self, num_concurrent: int = 10, total_requests: int = 100) -> LoadTestResult:
        """Run concurrent load test"""
        print(f"Starting concurrent load test: {num_concurrent} concurrent, {total_requests} total requests")
        
        results = []
        errors = []
        
        def run_request(request_id: int):
            """Run a single request"""
            request_text = self.test_requests[request_id % len(self.test_requests)]
            return self.single_request_test(request_text)
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            # Submit all requests
            futures = [executor.submit(run_request, i) for i in range(total_requests)]
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                    
                    if not result['success']:
                        errors.append(result.get('error', 'Unknown error'))
                        
                except Exception as e:
                    errors.append(str(e))
                    results.append({
                        'success': False,
                        'response_time': 0,
                        'error': str(e)
                    })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_results]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        error_rate = len(failed_results) / total_requests if total_requests > 0 else 0
        
        result = LoadTestResult(
            total_requests=total_requests,
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            errors=errors[:10]  # Limit error list
        )
        
        return result
    
    def stress_test(self, duration_seconds: int = 60, max_concurrent: int = 20) -> LoadTestResult:
        """Run stress test for specified duration"""
        print(f"Starting stress test: {duration_seconds} seconds, max {max_concurrent} concurrent")
        
        results = []
        errors = []
        start_time = time.time()
        request_count = 0
        
        def run_continuous_requests():
            """Run requests continuously"""
            nonlocal request_count
            
            while time.time() - start_time < duration_seconds:
                request_text = self.test_requests[request_count % len(self.test_requests)]
                result = self.single_request_test(request_text)
                results.append(result)
                
                if not result['success']:
                    errors.append(result.get('error', 'Unknown error'))
                
                request_count += 1
                time.sleep(0.1)  # Small delay to prevent overwhelming
        
        # Start concurrent threads
        threads = []
        for i in range(max_concurrent):
            thread = threading.Thread(target=run_continuous_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics (same as concurrent test)
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_results]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
            p99_response_time = statistics.quantiles(response_times, n=100)[98]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        requests_per_second = len(results) / total_time if total_time > 0 else 0
        error_rate = len(failed_results) / len(results) if results else 0
        
        return LoadTestResult(
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            errors=errors[:10]
        )
    
    def print_results(self, result: LoadTestResult, test_name: str):
        """Print load test results"""
        print(f"\n{'='*60}")
        print(f"{test_name} RESULTS")
        print(f"{'='*60}")
        print(f"Total Requests: {result.total_requests}")
        print(f"Successful: {result.successful_requests}")
        print(f"Failed: {result.failed_requests}")
        print(f"Success Rate: {(1 - result.error_rate) * 100:.1f}%")
        print(f"Error Rate: {result.error_rate * 100:.1f}%")
        print(f"Requests/Second: {result.requests_per_second:.2f}")
        print(f"\nResponse Times:")
        print(f"  Average: {result.average_response_time:.3f}s")
        print(f"  Min: {result.min_response_time:.3f}s")
        print(f"  Max: {result.max_response_time:.3f}s")
        print(f"  95th percentile: {result.p95_response_time:.3f}s")
        print(f"  99th percentile: {result.p99_response_time:.3f}s")
        
        if result.errors:
            print(f"\nSample Errors:")
            for i, error in enumerate(result.errors[:5]):
                print(f"  {i+1}. {error}")

def run_load_tests():
    """Run comprehensive load tests"""
    tester = LoadTester()
    
    print("🚀 Starting GiftPedia Load Tests")
    print("=" * 60)
    
    # Test 1: Single request baseline
    print("\n1. Single Request Baseline Test")
    baseline_result = tester.single_request_test(tester.test_requests[0])
    print(f"Baseline response time: {baseline_result['response_time']:.3f}s")
    print(f"Success: {baseline_result['success']}")
    
    # Test 2: Light load test
    print("\n2. Light Load Test (5 concurrent, 25 requests)")
    light_result = tester.concurrent_load_test(num_concurrent=5, total_requests=25)
    tester.print_results(light_result, "Light Load")
    
    # Test 3: Medium load test
    print("\n3. Medium Load Test (10 concurrent, 50 requests)")
    medium_result = tester.concurrent_load_test(num_concurrent=10, total_requests=50)
    tester.print_results(medium_result, "Medium Load")
    
    # Test 4: Heavy load test
    print("\n4. Heavy Load Test (20 concurrent, 100 requests)")
    heavy_result = tester.concurrent_load_test(num_concurrent=20, total_requests=100)
    tester.print_results(heavy_result, "Heavy Load")
    
    # Test 5: Stress test
    print("\n5. Stress Test (30 seconds, 15 concurrent)")
    stress_result = tester.stress_test(duration_seconds=30, max_concurrent=15)
    tester.print_results(stress_result, "Stress Test")
    
    # Summary
    print(f"\n{'='*60}")
    print("LOAD TEST SUMMARY")
    print(f"{'='*60}")
    
    all_results = [
        ("Light Load", light_result),
        ("Medium Load", medium_result),
        ("Heavy Load", heavy_result),
        ("Stress Test", stress_result)
    ]
    
    for test_name, result in all_results:
        print(f"{test_name:12} | {result.requests_per_second:6.2f} R/s | "
              f"{result.average_response_time:6.3f}s avg | "
              f"{result.error_rate*100:5.1f}% error")
    
    # Performance assessment
    print(f"\n📊 Performance Assessment:")
    
    # Check if performance meets requirements
    avg_rps = statistics.mean([r.requests_per_second for _, r in all_results])
    avg_response_time = statistics.mean([r.average_response_time for _, r in all_results])
    max_error_rate = max([r.error_rate for _, r in all_results])
    
    print(f"Average RPS: {avg_rps:.2f}")
    print(f"Average Response Time: {avg_response_time:.3f}s")
    print(f"Max Error Rate: {max_error_rate*100:.1f}%")
    
    # Performance thresholds
    if avg_rps >= 5.0:
        print("✅ RPS requirement met (≥5 RPS)")
    else:
        print("❌ RPS requirement not met (≥5 RPS)")
    
    if avg_response_time <= 5.0:
        print("✅ Response time requirement met (≤5s)")
    else:
        print("❌ Response time requirement not met (≤5s)")
    
    if max_error_rate <= 0.05:
        print("✅ Error rate requirement met (≤5%)")
    else:
        print("❌ Error rate requirement not met (≤5%)")

if __name__ == "__main__":
    import threading
    run_load_tests()
