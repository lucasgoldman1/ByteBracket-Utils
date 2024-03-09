import time
import boto3
from decimal import Decimal
import os
from boto3.dynamodb.conditions import Key
import redis
import json


client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')

league_brackets_table = dynamodb.Table('league_brackets')

redis_endpoint = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]

r = redis.Redis(host=redis_endpoint, port=redis_port)


def score_each_bracket(event, context):
    table = dynamodb.Table('brackets')
    master_bracket = table.get_item(
        Key={
            "username": "master",
            "id": "master"
        })
    master_bracket = master_bracket['Item']
    response = table.scan(
    )
    scoreAndUpdateBatch(response, master_bracket)
    while response.get('LastEvaluatedKey'):
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        scoreAndUpdateBatch(response, master_bracket)
        

def scoreAndUpdateBatch(response, master_bracket):
    count = 0
    for item in response['Items']:
        if item['username'] == 'master':
            continue
        leagues = league_brackets_table.query(
            IndexName='bracket-index',
            KeyConditionExpression=Key('bracket').eq(item['id']),
        )['Items']
        if not leagues:
            continue
        bracket = item
        points = 0
        for i, master_region in enumerate(master_bracket['bracket']):
            current_region = bracket['bracket'][i]
            for j, master_round in enumerate(master_region['rounds']):
                current_round = current_region['rounds'][j]
                if master_round['title'] == 64:
                    continue
                points_per_correct = 0
                if master_round['title'] == 32:
                    points_per_correct = 10
                elif master_round['title'] == 16:
                    points_per_correct = 20
                elif master_round['title'] == 8:
                    points_per_correct = 40
                elif master_round['title'] == 'finalfour':
                    points_per_correct = 80
                elif master_round['title'] == 'championship':
                    points_per_correct = 160
                for k, master_seeds in enumerate(master_round['seeds']):
                    current_seeds = current_round['seeds'][k]
                    if master_seeds[0] == current_seeds[0]:
                        points += points_per_correct
                    if master_seeds[1] == current_seeds[1]:
                        points += points_per_correct
        if bracket["champion"] == master_bracket["champion"]:
            points += 320
        for league in leagues:
            ind = json.dumps({"user": item["username"], "bracket": item["id"]})
            r.zadd(league['league'], {ind : points})
        count += 1
