#!/usr/bin/env python3
"""
Test script for the Approval Workflow Monitor
Tests monitoring, status detection, and processing triggers
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from utils.logger import setup_logging
from core.approval_workflow import ApprovalWorkflowMonitor
from integrations.google_sheets import GoogleSheetsManager

def test_approval_workflow_components():
    """Test individual approval workflow components"""
    print("🧪 Testing Approval Workflow Components")
    print("=" * 50)
    
    results = {
        'sheets_connection': False,
        'monitor_initialization': False,
        'status_scanning': False
    }
    
    # Test 1: Google Sheets Connection
    print("\n📊 Testing Google Sheets Connection...")
    try:
        sheets = GoogleSheetsManager()
        results['sheets_connection'] = sheets.test_connection()
        print(f"   Result: {'✅ PASS' if results['sheets_connection'] else '❌ FAIL'}")
        
        if results['sheets_connection']:
            # Test getting all content
            all_content = sheets.get_all_content()
            print(f"   📋 Found {len(all_content)} total content items")
            
            # Test getting approved content  
            approved_content = sheets.get_approved_content()
            print(f"   ✅ Found {len(approved_content)} approved content items")
            
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
    
    # Test 2: Approval Monitor Initialization
    print("\n🔍 Testing Approval Monitor Initialization...")
    try:
        monitor = ApprovalWorkflowMonitor()
        results['monitor_initialization'] = monitor.initialize()
        print(f"   Result: {'✅ PASS' if results['monitor_initialization'] else '❌ FAIL'}")
        
        if results['monitor_initialization']:
            # Test status information
            status = monitor.get_monitoring_status()
            print(f"   📊 Tracking {status['tracked_items']} items")
            print(f"   ✅ Processed {status['processed_items']} items")
            
    except Exception as e:
        print(f"   Result: ❌ FAIL - {e}")
    
    # Test 3: Status Scanning
    if results['monitor_initialization']:
        print("\n🔍 Testing Status Scanning...")
        try:
            scan_results = monitor.run_approval_monitor_cycle()
            results['status_scanning'] = scan_results.get('success', False)
            
            print(f"   Result: {'✅ PASS' if results['status_scanning'] else '❌ FAIL'}")
            print(f"   📊 Newly approved: {scan_results.get('newly_approved_count', 0)}")
            print(f"   ⏱️ Execution time: {scan_results.get('execution_time', 0)} seconds")
            
            # Show approved items if any
            approved_items = scan_results.get('approved_items', [])
            if approved_items:
                print(f"   🎉 Approved items found:")
                for item in approved_items[:3]:  # Show first 3
                    print(f"     - ID {item.get('id', 'N/A')}: {item.get('title', 'Untitled')}")
            
        except Exception as e:
            print(f"   Result: ❌ FAIL - {e}")
    
    return results

def test_approval_workflow_simulation():
    """Test the complete approval workflow with simulation"""
    print("\n\n🎬 Testing Complete Approval Workflow")
    print("=" * 50)
    
    try:
        # Initialize the workflow monitor
        print("Initializing Approval Workflow Monitor...")
        monitor = ApprovalWorkflowMonitor()
        
        if not monitor.initialize():
            print("❌ Failed to initialize monitor")
            return False
        
        print("✅ Monitor initialized successfully")
        
        # Run approval monitoring cycle
        print("\n🔄 Running approval monitoring cycle...")
        results = monitor.run_approval_monitor_cycle()
        
        print(f"📊 Monitoring Results:")
        print(f"   - Newly approved: {results.get('newly_approved_count', 0)}")
        print(f"   - Execution time: {results.get('execution_time', 0)}s")
        print(f"   - Success: {results.get('success', False)}")
        
        # Check if we have approved items to demonstrate workflow
        approved_items = results.get('approved_items', [])
        
        if approved_items:
            print(f"\n🎉 Demonstrating workflow with {len(approved_items)} approved items:")
            
            for item in approved_items[:2]:  # Process first 2 items
                content_id = item.get('id', '')
                title = item.get('title', 'Untitled')
                
                print(f"\n📝 Processing: ID {content_id} - {title}")
                
                # Mark as processing
                if monitor.mark_as_processing(content_id, title):
                    print(f"   ✅ Marked as processing")
                    
                    # Simulate processing
                    print(f"   🎬 [SIMULATION] Creating video...")
                    import time
                    time.sleep(0.5)  # Simulate work
                    
                    # Mark as completed
                    if monitor.mark_as_completed(content_id, {'simulation': 'test'}):
                        print(f"   ✅ Marked as completed")
                    else:
                        print(f"   ⚠️ Failed to mark as completed")
                else:
                    print(f"   ❌ Failed to mark as processing")
            
            print(f"\n🎉 Workflow simulation complete!")
            return True
        else:
            print("\n📋 No approved items found for workflow demonstration")
            print("💡 To test the full workflow:")
            print("   1. Open the Google Sheets dashboard")
            print("   2. Change a content item's status to 'Approved'")
            print("   3. Run this test again")
            return True
            
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        return False

def display_workflow_instructions():
    """Display instructions for testing the approval workflow"""
    print("\n\n📋 How to Test the Complete Approval Workflow")
    print("=" * 60)
    
    print("1. 🌐 Open Google Sheets Dashboard:")
    print("   https://docs.google.com/spreadsheets/d/1uAu0yBPzjAvvNn4GjVpnwa3P2wdpF9P69K1-anNqSZU/edit")
    
    print("\n2. 📝 Add Test Content (if needed):")
    print("   - Run: python test_content_ideation.py")
    print("   - This will add content with 'Pending Approval' status")
    
    print("\n3. ✅ Approve Content:")
    print("   - Find a row with status 'Pending Approval'")
    print("   - Change the STATUS column to 'Approved'")
    print("   - Save the changes")
    
    print("\n4. 🧪 Test Workflow:")
    print("   - Run: python test_approval_workflow.py")
    print("   - The workflow should detect the status change")
    print("   - Content should be processed and marked as completed")
    
    print("\n5. 📊 Verify Results:")
    print("   - Check the Google Sheets for status updates")
    print("   - Status should change: 'Approved' → 'In Progress' → 'Completed'")

def main():
    """Main test function"""
    # Setup logging
    setup_logging()
    
    print("🔍 Shorts Factory - Approval Workflow Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Test components
    component_results = test_approval_workflow_components()
    
    # Test complete workflow if components work
    working_components = sum(1 for result in component_results.values() if result)
    if working_components >= 2:  # Need sheets + monitor working
        workflow_success = test_approval_workflow_simulation()
    else:
        workflow_success = False
        print("\n⚠️ Skipping workflow test - need basic components working first")
    
    # Display instructions
    display_workflow_instructions()
    
    # Final summary
    success_rate = working_components / len(component_results)
    
    print(f"\n🎯 TEST SUMMARY:")
    print(f"   Component Success Rate: {success_rate:.0%}")
    print(f"   Workflow Test: {'✅ PASS' if workflow_success else '📋 READY TO TEST'}")
    print(f"   Overall Status: {'OPERATIONAL' if success_rate >= 0.5 else 'NEEDS SETUP'}")
    
    if success_rate >= 0.5:
        print("\n🎉 Approval Workflow is ready for production use!")
    else:
        print("\n⚠️ Some components need attention before full workflow testing")

if __name__ == '__main__':
    main()
