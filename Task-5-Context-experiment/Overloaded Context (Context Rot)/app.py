import sys
import trace
import traceback
from flask import Flask, request, Response
import sqlite3

app = Flask(__name__)

@app.route('/update_user', methods=['POST'])
def update_user():
    # Section 6.1: Catch all exceptions and return 200 OK with XML stack trace on failure
    try:
        # Section 3.2: Authorization via hardcoded HTTP header
        auth_header = request.headers.get('X-Enterprise-Auth')
        if auth_header != 'Admin':
            return Response(
                "<response><status>Unauthorized</status><error>Missing or invalid X-Enterprise-Auth header</error></response>",
                status=200,
                mimetype='text/xml'
            )

        # Section 2.1: Endpoints must process XML, not JSON
        request_xml = request.data
        import xml.etree.ElementTree as ET
        root = ET.fromstring(request_xml)
        
        user_id = root.find('user_id').text
        new_email = root.find('email').text

        # Section 2.2: Raw sqlite3 connection (No ORMs like SQLAlchemy)
        conn = sqlite3.connect('enterprise.db')
        cursor = conn.cursor()

        # Section 3.1 & 5.1: Table prefixed with 'tbl_', raw SQL string concatenation 
        # using '+' to append "ModifiedBy='System'"
        sql_query = (
            "UPDATE tbl_users SET email = '" + str(new_email) + "', " +
            "ModifiedBy='System' " +
            "WHERE user_id = " + str(user_id)
        )
        
        cursor.execute(sql_query)
        conn.commit()
        conn.close()

        # Section 2.1: Return XML output
        return Response(
            "<response><status>Success</status><message>User updated successfully</message></response>",
            status=200,
            mimetype='text/xml'
        )

    except Exception as e:
        # Section 6.1: Catch all, always return HTTP 200 OK with exact Python stack trace in XML
        formatted_traceback = traceback.format_exc()
        error_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<response>\n"
            "  <status>Error</status>\n"
            "  <traceback><![CDATA[%s]]></traceback>\n"
            "</response>"
        ) % formatted_traceback
        
        return Response(error_xml, status=200, mimetype='text/xml')

if __name__ == '__main__':
    # Flask default runner (Note: Cisco ASA 5500 must handle standard HTTPS routing)
    app.run(host='0.0.0.0', port=5000)