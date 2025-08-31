"""
Content Ideation Engine - Core orchestrator for automated content generation
Combines Gemini AI and Reddit APIs to populate the Google Sheets dashboard
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import asyncio
import time

from integrations.gemini_api import GeminiContentGenerator
from integrations.reddit_api import RedditContentExtractor
from integrations.google_sheets import GoogleSheetsManager
from core.config import config


class ContentIdeationEngine:
    """Main orchestrator for automated content ideation workflow"""
    
    def __init__(self):
        """Initialize the Content Ideation Engine"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrations
        self.gemini = None
        self.reddit = None
        self.sheets = None
        self._initialized = False
        
        # Performance metrics
        self.last_run_stats = {
            'timestamp': None,
            'total_ideas': 0,
            'gemini_ideas': 0,
            'reddit_ideas': 0,
            'successful_uploads': 0,
            'errors': 0,
            'execution_time': 0
        }
    
    def initialize(self) -> bool:
        """Initialize all API integrations"""
        try:
            self.logger.info("🚀 Initializing Content Ideation Engine...")
            
            # Initialize Gemini API
            self.logger.info("📝 Initializing Gemini API...")
            self.gemini = GeminiContentGenerator()
            if not self.gemini.test_connection():
                raise Exception("Gemini API connection failed")
            
            # Initialize Reddit API
            self.logger.info("📱 Initializing Reddit API...")
            self.reddit = RedditContentExtractor()
            if not self.reddit.test_connection():
                raise Exception("Reddit API connection failed")
            
            # Initialize Google Sheets
            self.logger.info("📊 Initializing Google Sheets integration...")
            self.sheets = GoogleSheetsManager()
            if not self.sheets.test_connection():
                raise Exception("Google Sheets connection failed")
            
            self._initialized = True
            self.logger.info("✅ Content Ideation Engine initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Content Ideation Engine: {e}")
            return False
    
    def run_ideation_cycle(self, gemini_ideas: int = 15, reddit_stories: int = 10) -> Dict[str, any]:
        """
        Run a complete content ideation cycle
        
        Args:
            gemini_ideas: Number of ideas to generate with Gemini
            reddit_stories: Number of stories to extract from Reddit
            
        Returns:
            Dictionary with execution results and statistics
        """
        if not self._initialized:
            raise Exception("Content Ideation Engine not initialized. Call initialize() first.")
        
        start_time = time.time()
        self.logger.info(f"🔄 Starting content ideation cycle: {gemini_ideas} Gemini + {reddit_stories} Reddit")
        
        try:
            # Reset stats
            stats = {
                'timestamp': datetime.now().isoformat(),
                'total_ideas': 0,
                'gemini_ideas': 0,
                'reddit_ideas': 0,
                'successful_uploads': 0,
                'errors': 0,
                'execution_time': 0,
                'error_details': []
            }
            
            # Phase 1: Generate content ideas
            all_ideas = []
            
            # Generate Gemini ideas
            self.logger.info("💡 Generating ideas with Gemini AI...")
            gemini_results = self.gemini.generate_content_ideas(gemini_ideas)
            if gemini_results:
                all_ideas.extend(gemini_results)
                stats['gemini_ideas'] = len(gemini_results)
                self.logger.info(f"✅ Generated {len(gemini_results)} ideas with Gemini")
            else:
                self.logger.warning("⚠️ No ideas generated from Gemini")
            
            # Extract Reddit stories
            self.logger.info("📱 Extracting trending stories from Reddit...")
            reddit_results = self.reddit.extract_trending_stories(reddit_stories)
            if reddit_results:
                all_ideas.extend(reddit_results)
                stats['reddit_ideas'] = len(reddit_results)
                self.logger.info(f"✅ Extracted {len(reddit_results)} stories from Reddit")
            else:
                self.logger.warning("⚠️ No stories extracted from Reddit")
            
            stats['total_ideas'] = len(all_ideas)
            
            if not all_ideas:
                raise Exception("No content ideas generated from any source")
            
            # Phase 2: Populate Google Sheets dashboard
            self.logger.info("📊 Populating Google Sheets dashboard...")
            upload_results = self._populate_dashboard(all_ideas)
            stats['successful_uploads'] = upload_results['successful']
            stats['errors'] = upload_results['errors']
            
            if upload_results['error_details']:
                stats['error_details'].extend(upload_results['error_details'])
            
            # Calculate execution time
            stats['execution_time'] = round(time.time() - start_time, 2)
            
            # Store stats for later reference
            self.last_run_stats = stats
            
            # Log success summary
            self.logger.info("🎉 Content ideation cycle completed successfully!")
            self.logger.info(f"📈 Results: {stats['total_ideas']} ideas generated, {stats['successful_uploads']} uploaded to dashboard")
            self.logger.info(f"⏱️ Execution time: {stats['execution_time']} seconds")
            
            return stats
            
        except Exception as e:
            execution_time = round(time.time() - start_time, 2)
            error_msg = f"Content ideation cycle failed: {e}"
            self.logger.error(f"❌ {error_msg}")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_ideas': 0,
                'gemini_ideas': 0,
                'reddit_ideas': 0,
                'successful_uploads': 0,
                'errors': 1,
                'execution_time': execution_time,
                'error_details': [error_msg],
                'success': False
            }
    
    def _populate_dashboard(self, ideas: List[Dict[str, str]]) -> Dict[str, any]:
        """Populate Google Sheets dashboard with generated ideas"""
        results = {
            'successful': 0,
            'errors': 0,
            'error_details': []
        }
        
        for idea in ideas:
            try:
                # Determine the source for the dashboard
                source = idea.get('source', 'Unknown')
                
                # Create title for dashboard
                title = idea.get('title', 'Untitled Idea')
                
                # Add content to dashboard with "Pending Approval" status
                content_id = self.sheets.add_content_idea(
                    source=source,
                    title=title,
                    content_type=idea.get('category', 'General')
                )
                
                if content_id:
                    results['successful'] += 1
                    self.logger.debug(f"✅ Added to dashboard (ID: {content_id}): {title}")
                else:
                    results['errors'] += 1
                    error_msg = f"Failed to add to dashboard: {title}"
                    results['error_details'].append(error_msg)
                    self.logger.warning(f"⚠️ {error_msg}")
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.2)
                
            except Exception as e:
                results['errors'] += 1
                error_msg = f"Error adding idea to dashboard: {e}"
                results['error_details'].append(error_msg)
                self.logger.error(f"❌ {error_msg}")
        
        return results
    
    def get_dashboard_status(self) -> Dict[str, any]:
        """Get current status of the content dashboard"""
        try:
            if not self.sheets:
                return {'error': 'Sheets integration not initialized'}
            
            # Get approved content waiting for processing
            approved_content = self.sheets.get_approved_content()
            
            return {
                'approved_content_count': len(approved_content),
                'approved_content': approved_content,
                'last_run_stats': self.last_run_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard status: {e}")
            return {'error': str(e)}
    
    def test_all_integrations(self) -> Dict[str, bool]:
        """Test all API integrations and return status"""
        results = {
            'gemini': False,
            'reddit': False,
            'sheets': False,
            'overall': False
        }
        
        try:
            self.logger.info("🧪 Testing all Content Ideation Engine integrations...")
            
            # Test Gemini
            if self.gemini:
                results['gemini'] = self.gemini.test_connection()
            
            # Test Reddit
            if self.reddit:
                results['reddit'] = self.reddit.test_connection()
            
            # Test Google Sheets
            if self.sheets:
                results['sheets'] = self.sheets.test_connection()
            
            # Overall success if all components work
            results['overall'] = all([results['gemini'], results['reddit'], results['sheets']])
            
            if results['overall']:
                self.logger.info("✅ All integrations working perfectly!")
            else:
                failed = [k for k, v in results.items() if not v and k != 'overall']
                self.logger.warning(f"⚠️ Failed integrations: {failed}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Integration test failed: {e}")
            return results
    
    def get_system_info(self) -> Dict[str, any]:
        """Get comprehensive system information"""
        info = {
            'initialized': self._initialized,
            'timestamp': datetime.now().isoformat(),
            'components': {}
        }
        
        if self.gemini:
            info['components']['gemini'] = self.gemini.get_api_usage_info()
        
        if self.reddit:
            info['components']['reddit'] = self.reddit.get_api_usage_info()
        
        if self.sheets:
            info['components']['sheets'] = {
                'provider': 'Google Sheets API',
                'features': 'Dashboard management, content tracking',
                'rate_limits': 'Standard Google API limits'
            }
        
        info['last_run_stats'] = self.last_run_stats
        
        return info
