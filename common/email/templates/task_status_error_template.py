__all__ = ["TaskStatusErrorTemplate"]
from common.constants.email_templates import TASK_STATUS_ERROR_TEMPLATE_NAME
from common.email.templates import BaseTemplate


class TaskStatusErrorTemplate(BaseTemplate):
    template_name: str = TASK_STATUS_ERROR_TEMPLATE_NAME
    subject: str = "Datakitchen - Task Error"
    required_args: list[str] = []
    content: str = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type"
        content="text/html; charset=utf-8"/>
  <meta name="viewport"
        content="width=device-width, initial-scale=1.0"/>
  <title>DataKitchen: Task Status Alert</title>
  <style type="text/css">
    body {
      margin: 0;
      padding: 0;
      background: #eeeeee !important;
    }

    h1, p {
      margin: 0;
    }

    .background {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background-color: #eeeeee;
    }

    .content {
      margin: 0 auto;
      background-color: white;
      font-family: 'Roboto', 'Helvetica Neue', sans-serif;
      font-size: 14px;
      line-height: 20px;
      color: rgba(0, 0, 0, 0.87);
      width: 100%;
      min-width: 500px;
      max-width: 800px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 1px rgba(0, 0, 0, 0.14), 0 2px 1px rgba(0, 0, 0, 0.02);
    }

    .header {
      width: 100%;
      margin: 20px 32px 0;
    }

    .logo {
      width: 124px;
      vertical-align: top;
      padding-top: 4px;
      padding-left: 0;
    }

    .logo--full {
      height: 24px;
    }

    .logo--icon {
      height: 40px;
      display: none;
    }

    .title {
      font-size: 20px;
      line-height: 23px;
      white-space: nowrap;
      text-align: center;
      margin-bottom: 4px;
      padding-right: 124px;
      color: rgba(0, 0, 0, 0.87);
    }

    .title__status {
      color: #F44336;
      font-size: 28px;
      line-height: 20px;
      vertical-align: middle;
      font-family: Arial sans-serif;
    }

    .summary {
      padding: 4px 16px 16px;
      border: 1px solid rgba(0, 0, 0, 0.12);
      border-radius: 4px;
      margin: 8px 32px 4px;
    }

    .summary > table {
      width: 100%;
    }

    .summary__title {
      height: 28px;
      color: rgba(0, 0, 0, 0.87);
    }

    .summary__label {
      line-height: 16px;
      color: rgba(0, 0, 0, 0.54);
      width: 100px;
      height: 20px;
    }

    .summary__value {
      padding-left: 8px;
    }

    .link {
      color: #1976D2 !important;
      cursor: pointer !important;
      text-decoration: none;
    }

    .footer {
      color: rgba(0, 0, 0, 0.38);
      font-size: 12px;
    }

    .footer td {
      height: 52px;
      background-color: #FAFAFA;
      padding: 0 24px;
    }

    .footer a {
      color: rgba(0, 0, 0, 0.38) !important;
      border-bottom: 1px solid rgba(0, 0, 0, 0.38);
      text-decoration: none;
    }

    .footer__padding {
      height: 32px;
    }

    @media screen and (max-width: 600px) {
      .background__cell {
        padding: 0;
      }

      .content {
        border-width: 16px 16px 8px;
        font-size: 16px;
      }

      .logo {
        width: 44px;
        padding-top: 5px;
      }

      .logo--full {
        display: none;
      }

      .logo--icon {
        display: block;
      }
    }

    /* Remove space around the email design. */
    html,
    body {
      margin: 0 auto !important;
      padding: 0 !important;
      height: 100% !important;
      width: 100% !important;
    }

    /* Stop Outlook resizing small text. */
    * {
      -ms-text-size-adjust: 100%;
    }

    /* Stop Outlook from adding extra spacing to tables. */
    table,
    td {
      mso-table-lspace: 0pt !important;
      mso-table-rspace: 0pt !important;
    }

    /* Use a better rendering method when resizing images in Outlook IE. */
    img {
      -ms-interpolation-mode: bicubic;
    }
  </style>
</head>
<body>

<!-- BACKGROUND -->
<table role="presentation"
       cellpadding="32"
       cellspacing="0"
       border="0"
       class="background">
  <tr>
    <td class="background__cell">
      <!-- CONTENT -->
      <table role="presentation"
             cellpadding="2"
             cellspacing="0"
             border="0"
             class="content">

        <!-- HEADER -->
        <tr>
          <td colspan="2">
            <table role="presentation"
                   cellpadding="2"
                   cellspacing="0"
                   border="0"
                   class="header">
              <tr>
                <!-- LOGO -->
                <td class="logo">
                  <!-- for regular screens -->
                  <img
                    src="https://dk-support-external.s3.amazonaws.com/support/dk_logo_horizontal.png"
                    alt="DataKitchen Logo"
                    height="24"
                    class="logo--full">

                  <!-- for smaller screens -->
                  <!--[if !mso]><!-->
                  <img
                    src="https://dk-support-external.s3.amazonaws.com/support/dk_logo.png"
                    alt="DataKitchen Logo"
                    height="40"
                    class="logo--icon">
                  <!--<![endif]-->
                </td>
                <!-- TITLE -->
                <td class="title">
                  Task Failed&nbsp;<span
                  class="title__status"><span>&#8226;</span></span>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <tr>
          <td colspan="2" style="white-space: nowrap">
            <!-- SUMMARY -->
            <div class="summary">
              <table
                role="presentation"
                cellpadding="2"
                cellspacing="0"
                border="0">
                <tr>
                  <td colspan="2"
                      class="summary__title">Summary
                  </td>
                </tr>
                <tr>
                  <td class="summary__label">Project</td>
                  <td class="summary__value">{{ project_name }}</td>
                </tr>
                <tr>
                  <td class="summary__label">Journey</td>
                  <td class="summary__value">{{ journey_name }}</td>
                </tr>
                <tr>
                  <td class="summary__label">Pipeline</td>
                  <td class="summary__value">{{ component_name }}</td>
                </tr>
                <tr>
                  <td class="summary__label">Run</td>
                  <td class="summary__value">
                    <a
                      href="https://{{ base_url }}/projects/{{ project_id }}/events/runs/details/{{ run_id }}/events"
                      target="_blank">
                      {{#if run_key}}
                      {{ run_key }}
                      {{else}}
                      {{ run_id }}
                      {{/if}}
                    </a>
                  </td>
                </tr>
                <tr>
                  <td class="summary__label">Task</td>
                  <td class="summary__value">{{ task_name }}</td>
                </tr>
                <tr>
                  <td class="summary__label">Task Status</td>
                  <td class="summary__value">Error</td>
                </tr>
                <tr>
                  <td class="summary__label">Start Time</td>
                  <td class="summary__value">{{ run_task_start_time }}</td>
                </tr>
                <tr>
                  <td class="summary__label">Event Timestamp</td>
                  <td class="summary__value">{{ event_timestamp_formatted }}</td>
                </tr>
              </table>
            </div>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td colspan="2"
              class="footer__padding"></td>
        </tr>
        <tr class="footer">
          <td>DataKitchen Alert Email</td>
          <td align="right">
            <a href="http://datakitchen.io"
               target="_blank"
               title="DataKitchen website">datakitchen.io</a>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""
