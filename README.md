# nagios-teams-notify
Send Nagios alerts to a Microsoft Teams channel

## Overview

This script can send Nagios alerts to a Microsoft Teams channel.

By sending alerts to Teams, we can simplify addition and removal alert recipients, allow for self-service subscription and push preferences, and have conversations based around the alerts as they occur.

## Installation

Install dependancies from requirements.txt and place `host-notify-teams.py` and `service-notify-teams.py` where they can be executed by the Nagios user. Make the scripts executable with `chmod +x host-notify-teams.py service-notify-teams.py`.

## Configuration

### Create the Webhook

From [Using Office 365 Connectors: Teams](https://docs.microsoft.com/en-us/microsoftteams/platform/concepts/connectors/connectors-using#setting-up-a-custom-incoming-webhook):

1. In Microsoft Teams, choose More options (⋯) next to the channel name and then choose Connectors.
2. Scroll through the list of Connectors to Incoming Webhook, and choose Add.
3. Enter a name for the webhook, upload an image to associate with data from the webhook, and choose Create.
4. Copy the webhook to the clipboard and save it. You'll need the webhook URL for sending information to Microsoft Teams.
5. Choose Done.

### Configure Nagios

Create command objects in the Nagios configuration.

```
define command {
    command_name    notify-host-by-teams
    command_line    /usr/bin/printf "$LONGSERVICEOUTPUT$" | $USER1$/nagios-teams-notify/host-notify-teams.py  "$NOTIFICATIONTYPE$" "$HOSTNAME$" "$HOSTALIAS$" "$SERVICEDESC$" "$SERVICESTATE$" "$SERVICEOUTPUT$" $_CONTACT_WEBHOOKURL$
}
```
```
define command {
    command_name    notify-service-by-teams
    command_line    /usr/bin/printf "$LONGSERVICEOUTPUT$" | $USER1$/nagios-teams-notify/service-notify-teams.py  "$NOTIFICATIONTYPE$" "$HOSTNAME$" "$HOSTALIAS$" "$SERVICEDESC$" "$SERVICESTATE$" "$SERVICEOUTPUT$" $_CONTACT_WEBHOOKURL$
}
```

Create a contact object with the custom variable macro __WEBHOOK set to the URL from the Teams channel connector. This variable is used when running the command above.

```
define contact {
    contact_name    example-team
    alias           Example Team
    host_notifications_enabled  1
    service_notifications_enabled   1
    host_notification_period	24x7
    service_notification_period	24x7 
    host_notification_options	d,u,r,f
    service_notification_options	w,u,c,r,f
    host_notification_commands	notify_teams
    service_notification_commands	notify_teams
    __WEBHOOKURL https://webhookurl_generated_by_teams
    }
```

Then add the contact to an existing object or contact group and reload your configuration.

Create additional contacts with their own `__WEBHOOKURL` custom variable macro for each Teams channel needing notifications.
