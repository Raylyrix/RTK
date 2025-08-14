import schedule
import time
import threading
import datetime
import json
import os
from email_sender import EmailSender
from sheets_handler import SheetsHandler
import config

class EmailScheduler:
    def __init__(self):
        self.scheduled_jobs = []
        self.scheduler_thread = None
        self.running = False
        self.jobs_file = config.BASE_DIR / "scheduled_jobs.json"
        self.load_jobs()
    
    def load_jobs(self):
        """Load scheduled jobs from file"""
        try:
            if os.path.exists(self.jobs_file):
                with open(self.jobs_file, 'r') as f:
                    jobs_data = json.load(f)
                    for job_data in jobs_data:
                        self.schedule_job_from_data(job_data)
        except Exception as e:
            print(f"Error loading jobs: {e}")
    
    def save_jobs(self):
        """Save scheduled jobs to file"""
        try:
            jobs_data = []
            for job in self.scheduled_jobs:
                jobs_data.append({
                    'id': job['id'],
                    'name': job['name'],
                    'schedule_type': job['schedule_type'],
                    'schedule_time': job['schedule_time'],
                    'template_subject': job['template_subject'],
                    'template_body': job['template_body'],
                    'template_html': job['template_html'],
                    'sheet_url': job['sheet_url'],
                    'sheet_name': job['sheet_name'],
                    'batch_size': job['batch_size'],
                    'time_gap': job['time_gap'],
                    'created_at': job['created_at'],
                    'status': job['status']
                })
            
            with open(self.jobs_file, 'w') as f:
                json.dump(jobs_data, f, indent=2)
        except Exception as e:
            print(f"Error saving jobs: {e}")
    
    def create_scheduled_job(self, name, schedule_type, schedule_time, 
                           template_subject, template_body, template_html,
                           sheet_url, sheet_name, batch_size, time_gap):
        """Create a new scheduled job"""
        
        job_id = f"job_{int(time.time())}"
        
        job_data = {
            'id': job_id,
            'name': name,
            'schedule_type': schedule_type,  # 'once', 'daily', 'weekly', 'monthly'
            'schedule_time': schedule_time,  # datetime string or time string
            'template_subject': template_subject,
            'template_body': template_body,
            'template_html': template_html,
            'sheet_url': sheet_url,
            'sheet_name': sheet_name,
            'batch_size': batch_size,
            'time_gap': time_gap,
            'created_at': datetime.datetime.now().isoformat(),
            'status': 'active'
        }
        
        if self.schedule_job_from_data(job_data):
            self.scheduled_jobs.append(job_data)
            self.save_jobs()
            return job_id
        
        return None
    
    def schedule_job_from_data(self, job_data):
        """Schedule a job from job data"""
        try:
            def job_function():
                self.execute_scheduled_job(job_data)
            
            schedule_type = job_data['schedule_type']
            schedule_time = job_data['schedule_time']
            
            if schedule_type == 'once':
                # Parse datetime string
                target_datetime = datetime.datetime.fromisoformat(schedule_time)
                if target_datetime > datetime.datetime.now():
                    # Schedule for specific date/time
                    schedule.every().day.at(target_datetime.strftime('%H:%M')).do(job_function).tag(job_data['id'])
            elif schedule_type == 'daily':
                schedule.every().day.at(schedule_time).do(job_function).tag(job_data['id'])
            elif schedule_type == 'weekly':
                # Assuming schedule_time format is "monday 10:30"
                day, time_str = schedule_time.split(' ')
                getattr(schedule.every(), day.lower()).at(time_str).do(job_function).tag(job_data['id'])
            elif schedule_type == 'monthly':
                # For monthly, we'll check on daily basis and execute if it's the right day
                schedule.every().day.at(schedule_time).do(
                    lambda: self.monthly_job_check(job_data)
                ).tag(job_data['id'])
            
            return True
            
        except Exception as e:
            print(f"Error scheduling job {job_data['id']}: {e}")
            return False
    
    def monthly_job_check(self, job_data):
        """Check if monthly job should run today"""
        today = datetime.date.today()
        if today.day == 1:  # Run on first day of month
            self.execute_scheduled_job(job_data)
    
    def execute_scheduled_job(self, job_data):
        """Execute a scheduled email job"""
        try:
            print(f"Executing scheduled job: {job_data['name']}")
            
            # Get data from Google Sheets
            sheets_handler = SheetsHandler()
            sheet_data = sheets_handler.get_sheet_data(job_data['sheet_url'], job_data['sheet_name'])
            
            if not sheet_data or not sheet_data.get('data'):
                print(f"No data found for job {job_data['name']}")
                return
            
            # Send emails
            email_sender = EmailSender()
            sent, failed = email_sender.send_bulk_emails(
                sheet_data,
                job_data['template_subject'],
                job_data['template_body'],
                job_data['template_html'],
                job_data['batch_size'],
                job_data['time_gap']
            )
            
            # Log results
            print(f"Job {job_data['name']} completed: {sent} sent, {failed} failed")
            
            # If it's a 'once' job, mark as completed
            if job_data['schedule_type'] == 'once':
                job_data['status'] = 'completed'
                schedule.clear(job_data['id'])
                self.save_jobs()
            
        except Exception as e:
            print(f"Error executing job {job_data['id']}: {e}")
    
    def start_scheduler(self):
        """Start the scheduler thread"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            print("Email scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("Email scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def get_scheduled_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduled_jobs
    
    def cancel_job(self, job_id):
        """Cancel a scheduled job"""
        try:
            schedule.clear(job_id)
            self.scheduled_jobs = [job for job in self.scheduled_jobs if job['id'] != job_id]
            self.save_jobs()
            return True
        except Exception as e:
            print(f"Error canceling job {job_id}: {e}")
            return False
    
    def get_next_run_time(self, job_id):
        """Get next run time for a job"""
        try:
            jobs = schedule.get_jobs(job_id)
            if jobs:
                return jobs[0].next_run
        except:
            pass
        return None 