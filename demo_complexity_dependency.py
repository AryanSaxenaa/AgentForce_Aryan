#!/usr/bin/env python3
"""
Demo script showcasing enhanced complexity and dependency analysis capabilities.
"""

from src.analyzers.complexity_analyzer import ComplexityAnalyzer
from src.analyzers.dependency_analyzer import DependencyAnalyzer


def demo_complexity_analysis():
    """Demonstrate complexity analysis capabilities."""
    print("=" * 60)
    print("COMPLEXITY ANALYSIS DEMO")
    print("=" * 60)
    
    analyzer = ComplexityAnalyzer()
    
    # Simple function
    simple_code = """
def add(a, b):
    return a + b
"""
    
    # Complex function with nested loops and conditions
    complex_code = """
def complex_algorithm(data_matrix):
    result = []
    total = 0
    
    for i in range(len(data_matrix)):
        for j in range(len(data_matrix[i])):
            for k in range(len(data_matrix[i][j])):
                value = data_matrix[i][j][k]
                
                if value > 0:
                    if value % 2 == 0:
                        while value > 1:
                            value //= 2
                            total += value
                    elif value % 3 == 0:
                        total += value * 3
                    else:
                        total += value
                elif value < 0:
                    total -= abs(value)
                
                result.append(total)
    
    return result, total
"""
    
    # Recursive function
    recursive_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    
    print("\n1. Simple Function Analysis:")
    simple_metrics = analyzer.analyze(simple_code)
    print(f"   Cyclomatic Complexity: {simple_metrics.cyclomatic_complexity}")
    print(f"   Cognitive Complexity: {simple_metrics.cognitive_complexity}")
    print(f"   Lines of Code: {simple_metrics.lines_of_code}")
    print(f"   Maintainability Index: {simple_metrics.maintainability_index}")
    
    print("\n2. Complex Function Analysis:")
    complex_metrics = analyzer.analyze(complex_code)
    print(f"   Cyclomatic Complexity: {complex_metrics.cyclomatic_complexity}")
    print(f"   Cognitive Complexity: {complex_metrics.cognitive_complexity}")
    print(f"   Lines of Code: {complex_metrics.lines_of_code}")
    print(f"   Maintainability Index: {complex_metrics.maintainability_index}")
    
    print("\n3. Recursive Function Analysis:")
    recursive_metrics = analyzer.analyze(recursive_code)
    print(f"   Cyclomatic Complexity: {recursive_metrics.cyclomatic_complexity}")
    print(f"   Cognitive Complexity: {recursive_metrics.cognitive_complexity}")
    print(f"   Lines of Code: {recursive_metrics.lines_of_code}")
    print(f"   Maintainability Index: {recursive_metrics.maintainability_index}")
    
    print("\n4. Complexity Comparison:")
    print(f"   Simple vs Complex Cyclomatic: {simple_metrics.cyclomatic_complexity} vs {complex_metrics.cyclomatic_complexity}")
    print(f"   Simple vs Complex Maintainability: {simple_metrics.maintainability_index} vs {complex_metrics.maintainability_index}")


def demo_dependency_analysis():
    """Demonstrate dependency analysis capabilities."""
    print("\n" + "=" * 60)
    print("DEPENDENCY ANALYSIS DEMO")
    print("=" * 60)
    
    analyzer = DependencyAnalyzer()
    
    # Python code with various dependencies
    python_code = """
import os
import sys
import json
from typing import List, Dict, Optional
from collections import defaultdict
import requests
import sqlite3
import asyncio
import aiohttp
from flask import Flask, request, jsonify

app = Flask(__name__)

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

def save_to_database(data):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO data VALUES (?)', (json.dumps(data),))
    conn.commit()
    conn.close()

@app.route('/api/data')
def get_data():
    data = requests.get('https://api.example.com/data').json()
    save_to_database(data)
    return jsonify(data)
"""
    
    # JavaScript code with dependencies
    js_code = """
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
const express = require('express');
const fs = require('fs');
const path = require('path');

function DataComponent() {
    const [data, setData] = useState(null);
    
    useEffect(() => {
        axios.get('/api/data')
            .then(response => setData(response.data))
            .catch(error => console.error(error));
    }, []);
    
    return <div>{JSON.stringify(data)}</div>;
}

const app = express();
app.use(express.static(path.join(__dirname, 'public')));
"""
    
    # Java code with dependencies
    java_code = """
import java.util.List;
import java.util.ArrayList;
import java.io.File;
import java.io.FileReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class DataController {
    
    @GetMapping("/api/data")
    public List<String> getData() {
        List<String> data = new ArrayList<>();
        
        try {
            Connection conn = DriverManager.getConnection("jdbc:sqlite:app.db");
            PreparedStatement stmt = conn.prepareStatement("SELECT * FROM data");
            // ... database operations
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        return data;
    }
}
"""
    
    print("\n1. Python Dependencies:")
    python_deps = analyzer.detect(python_code, 'python')
    for dep in python_deps:
        print(f"   {dep.name} ({dep.type})")
    
    print(f"\n   Total Python dependencies: {len(python_deps)}")
    
    print("\n2. JavaScript Dependencies:")
    js_deps = analyzer.detect(js_code, 'javascript')
    for dep in js_deps:
        print(f"   {dep.name} ({dep.type})")
    
    print(f"\n   Total JavaScript dependencies: {len(js_deps)}")
    
    print("\n3. Java Dependencies:")
    java_deps = analyzer.detect(java_code, 'java')
    for dep in java_deps:
        print(f"   {dep.name} ({dep.type})")
    
    print(f"\n   Total Java dependencies: {len(java_deps)}")
    
    print("\n4. Dependency Risk Analysis:")
    python_risks = analyzer.analyze_dependency_complexity(python_deps)
    if python_risks:
        print("   Python risks detected:")
        for risk in python_risks:
            print(f"   - {risk.type}: {risk.description} (Severity: {risk.severity})")
    else:
        print("   No significant dependency risks detected in Python code")
    
    js_risks = analyzer.analyze_dependency_complexity(js_deps)
    if js_risks:
        print("   JavaScript risks detected:")
        for risk in js_risks:
            print(f"   - {risk.type}: {risk.description} (Severity: {risk.severity})")
    else:
        print("   No significant dependency risks detected in JavaScript code")


def demo_integration():
    """Demonstrate integration of complexity and dependency analysis."""
    print("\n" + "=" * 60)
    print("INTEGRATED ANALYSIS DEMO")
    print("=" * 60)
    
    complexity_analyzer = ComplexityAnalyzer()
    dependency_analyzer = DependencyAnalyzer()
    
    # Complex code with many dependencies
    integrated_code = """
import requests
import sqlite3
import asyncio
import aiohttp
from typing import List, Dict
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import time

class DataProcessor:
    def __init__(self, db_path: str, max_workers: int = 10):
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(__name__)
    
    async def process_urls_batch(self, urls: List[str]) -> Dict[str, any]:
        results = {}
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Complex nested processing
                            for category in data.get('categories', []):
                                for item in category.get('items', []):
                                    for detail in item.get('details', []):
                                        if detail.get('active', False):
                                            if detail.get('priority', 0) > 5:
                                                while detail.get('processing_queue', 0) > 0:
                                                    detail['processing_queue'] -= 1
                                                    if detail['processing_queue'] % 10 == 0:
                                                        await asyncio.sleep(0.1)
                                            
                                            results[detail.get('id')] = detail
                        else:
                            self.logger.warning(f"Failed to fetch {url}: {response.status}")
                            
                except asyncio.TimeoutError:
                    self.logger.error(f"Timeout fetching {url}")
                except Exception as e:
                    self.logger.error(f"Error processing {url}: {e}")
        
        # Save to database
        await self.save_results(results)
        return results
    
    async def save_results(self, results: Dict[str, any]):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            for result_id, data in results.items():
                cursor.execute(
                    'INSERT OR REPLACE INTO results (id, data, timestamp) VALUES (?, ?, ?)',
                    (result_id, json.dumps(data), time.time())
                )
            conn.commit()
        finally:
            conn.close()
    
    def recursive_data_transform(self, data: Dict, depth: int = 0) -> Dict:
        if depth > 10:  # Prevent infinite recursion
            return data
        
        transformed = {}
        for key, value in data.items():
            if isinstance(value, dict):
                transformed[key] = self.recursive_data_transform(value, depth + 1)
            elif isinstance(value, list):
                transformed[key] = [
                    self.recursive_data_transform(item, depth + 1) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                transformed[key] = value
        
        return transformed
"""
    
    print("\n1. Complexity Analysis of Integrated Code:")
    complexity_metrics = complexity_analyzer.analyze(integrated_code)
    print(f"   Cyclomatic Complexity: {complexity_metrics.cyclomatic_complexity}")
    print(f"   Cognitive Complexity: {complexity_metrics.cognitive_complexity}")
    print(f"   Lines of Code: {complexity_metrics.lines_of_code}")
    print(f"   Maintainability Index: {complexity_metrics.maintainability_index}")
    
    print("\n2. Dependency Analysis of Integrated Code:")
    dependencies = dependency_analyzer.detect(integrated_code, 'python')
    print(f"   Total dependencies: {len(dependencies)}")
    
    # Group dependencies by type
    dep_by_type = {}
    for dep in dependencies:
        dep_type = dep.type
        if dep_type not in dep_by_type:
            dep_by_type[dep_type] = []
        dep_by_type[dep_type].append(dep.name)
    
    for dep_type, names in dep_by_type.items():
        print(f"   {dep_type}: {', '.join(names)}")
    
    print("\n3. Risk Assessment:")
    risks = dependency_analyzer.analyze_dependency_complexity(dependencies)
    if risks:
        for risk in risks:
            print(f"   - {risk.type}: {risk.description} (Severity: {risk.severity})")
    else:
        print("   No significant risks detected")
    
    print("\n4. Overall Assessment:")
    if complexity_metrics.cyclomatic_complexity > 15:
        print("   ⚠️  High complexity detected - consider refactoring")
    elif complexity_metrics.cyclomatic_complexity > 10:
        print("   ⚡ Moderate complexity - monitor for growth")
    else:
        print("   ✅ Acceptable complexity level")
    
    if len(dependencies) > 15:
        print("   ⚠️  Many dependencies - review for necessity")
    elif len(dependencies) > 10:
        print("   ⚡ Moderate dependency count - monitor additions")
    else:
        print("   ✅ Reasonable dependency count")
    
    if complexity_metrics.maintainability_index < 50:
        print("   ⚠️  Low maintainability - refactoring recommended")
    elif complexity_metrics.maintainability_index < 70:
        print("   ⚡ Moderate maintainability - consider improvements")
    else:
        print("   ✅ Good maintainability")


if __name__ == "__main__":
    print("Enhanced Complexity and Dependency Analysis Demo")
    print("This demo showcases the improved AST-based analysis capabilities")
    
    demo_complexity_analysis()
    demo_dependency_analysis()
    demo_integration()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nKey improvements implemented:")
    print("✅ AST-based complexity analysis with proper nesting consideration")
    print("✅ Enhanced dependency detection including external calls and file operations")
    print("✅ Performance risk detection for loops, recursion, and complex operations")
    print("✅ Comprehensive dependency categorization and risk assessment")
    print("✅ Multi-language support with language-specific patterns")
    print("✅ Maintainability index calculation using industry-standard formulas")
    print("✅ Extensive unit test coverage with integration tests")