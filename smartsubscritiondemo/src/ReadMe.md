in pyharm projects just open terminal

1.Terminate instance running int he last 5 minutes
http://127.0.0.1:5000/terminate-instances
2. default create Instance-
http://127.0.0.1:5000/create_ec2_instance
no payload
3. For given imge ID create Instance-
http://127.0.0.1:5000/create-instances-for-image-id
payload as 
{
  "image_id": "ami-0889a44b331db0194"
}
========
4. For demo, all stopped instances for the past 5 minutes terminated
 to test.
Setup:
   1. Create instance
   2. print_ec2details - observe state and instance id
   3. stop instance
   4. print_ec2details - observe state
   5. run program for every minute-cron job check_instance_status_periodically

walk-thru
   6. Wait for 2 minutes
   7. print_ec2details - observe state and instance id
8. ===================
9. TO DO
10. Greetings
11. showreenformcentalgorithm in the moniorAPI
   