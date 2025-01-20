import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from typing import List

load_dotenv()

def send_scandinavian_newsletter(
    recipients: List[str],
    subject: str,
    news_categories: dict[str, List[str]],
    header_image_url: str|None = None,
    from_email: str="dominique@palta-labs.com",
    api_key: str = os.environ["SENDGRID_API_KEY"],
) -> dict:
    """
    Send a Swedish-style newsletter to multiple recipients.
    
    Args:
        api_key: SendGrid API key
        from_email: Verified sender email
        recipients: List of recipient emails
        subject: Email subject line
        news_categories: Dict of category/heading -> list of news items
        header_image_url: Optional URL to header image
    
    Returns:
        dict: Status codes for each recipient
    """
    
    # Format news sections
    news_sections_html = ""
    for category, items in news_categories.items():
        # Convert each item's newlines to <br> tags and properly format bullet points
        items_html = "\n".join([
            f'''<li class="news-item">{
                item.strip().replace('\n', '<br>')
            }</li>''' 
            for item in items
        ])
        news_sections_html += f'''
            <div class="news-section">
                <h2 class="category-header">{category}</h2>
                <ul class="news-list">
                    {items_html}
                </ul>
            </div>
        '''

    html = f'''
    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600&display=swap');
            
            body {{
                font-family: 'Crimson Pro', serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
                color: #1a1a1a;
            }}
            
            .container {{
                max-width: 700px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            
            .content-wrapper {{
                background-color: #ffffff;
                padding: 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            .header {{
                text-align: center;
                padding: 40px 40px 20px;
            }}
            
            .header-image {{
                width: 100%;
                height: auto;
                margin-bottom: 24px;
            }}
            
            .header h1 {{
                margin: 0;
                font-size: 32px;
                font-weight: 600;
                color: #1a1a1a;
                letter-spacing: -0.5px;
            }}
            
            .date {{
                color: #666666;
                font-size: 14px;
                margin-top: 12px;
                font-style: italic;
            }}
            
            .content {{
                padding: 20px 40px 40px;
            }}
            
            .news-section {{
                margin-bottom: 40px;
            }}
            
            .category-header {{
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 16px;
                color: #1a1a1a;
                border-bottom: 2px solid #e60012;
                padding-bottom: 8px;
            }}
            
            .news-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            
            .news-item {{
                position: relative;
                padding: 12px 0 12px 24px;
                font-size: 16px;
                line-height: 1.7;
                margin-bottom: 16px;  /* Add spacing between items */
                text-align: left;     /* Ensure left alignment */
            }}
            
            .news-item br {{
                margin-top: 8px;      /* Add spacing between paragraphs */
                display: block;
                content: "";
            }}
            
            .news-item::before {{
                content: "•";
                position: absolute;
                left: 0;
                color: #e60012;
                font-weight: bold;
            }}
            
            .footer {{
                padding: 24px 40px;
                background-color: #f8f8f8;
                text-align: center;
                font-size: 13px;
                color: #666666;
                border-top: 1px solid #eeeeee;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    padding: 20px 16px;
                }}
                
                .header, .content, .footer {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content-wrapper">
                <div class="header">
                    {f'<img src="{header_image_url}" class="header-image" alt="Newsletter header image">' if header_image_url else ''}
                    <h1>{subject}</h1>
                    <div class="date">{datetime.now().strftime('%d %B %Y')}</div>
                </div>
                
                <div class="content">
                    {news_sections_html}
                </div>
                
                <div class="footer">
                    Set up your own personalised newsletter sent at your schedule.
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

    results = {}
    try:
        sg = SendGridAPIClient(api_key)
        
        # Send to each recipient individually for personalization
        for recipient in recipients:
            message = Mail(
                from_email=from_email,
                to_emails=recipient,
                subject=subject,
                html_content=html
            )
            
            response = sg.send(message)
            results[recipient] = response.status_code
            print(f"Sent to {recipient} - Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error sending newsletter: {e}")
        
    return results

# Example usage
if __name__ == "__main__":
    
    # Example data
    recipients = [
        "dominique.paul.info@gmail.com"
    ]
    
    subject = "Your Weekly Update"
    
    news_categories = {
        "Technology": [
            "Our new product launched today, featuring innovative design and sustainable materials",
            "Join us for our upcoming workshop on sustainable design practices next month",
            "We've been featured in Design Weekly magazine's 'Top 10 Innovative Companies'",
            "Our team is expanding - we're looking for creative minds to join us"
        ],
        "Design": [
            "Our new product launched today, featuring innovative design and sustainable materials",
            "Join us for our upcoming workshop on sustainable design practices next month",
            "We've been featured in Design Weekly magazine's 'Top 10 Innovative Companies'",
            "Our team is expanding - we're looking for creative minds to join us"
        ],
        "Sustainability": [
            "Our new product launched today, featuring innovative design and sustainable materials",
            "Join us for our upcoming workshop on sustainable design practices next month",
            "We've been featured in Design Weekly magazine's 'Top 10 Innovative Companies'",
            "Our team is expanding - we're looking for creative minds to join us"
        ]
    }
    
    # Send the newsletter
    results = send_scandinavian_newsletter(
        recipients=recipients,
        subject=subject,
        news_categories=news_categories,
        header_image_url="https://example.com/header-image.jpg"
    )
