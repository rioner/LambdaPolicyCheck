# coding:utf-8
import boto3
import json

# メイン
def lambda_handler(event, context):
    
    # DynamoDBからLambdaポリシーでアクセスを可能とするアカウントIDを取得
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('テーブル名')
    response = table.scan()
    list_accounts = []
    for res in response['Items']:
        list_accounts.append(res['account_id'])
    # lambda取得
    client = boto3.client('lambda')
    # print用
    message = ""
    # Lambda関数取得
    functions = client.list_functions()['Functions']
    for function in functions:
        # 関数名出力
        print(function['FunctionName'])
        try:
            # 関数ポリシー取得
            response = client.get_policy(FunctionName=function['FunctionName'])
            for principal in json.loads(response['Policy'])['Statement']:
                if 'AWS' in principal['Principal']:
                    # 例外リストにないアカウントに許可設定があった場合は開けすぎ判定を出す
                    for account in list_accounts:
                        # principal['Principal']['AWS']（例：arn:aws:iam::xxxxxxxxxxxx:root）
                        if account in principal['Principal']['AWS']:
                            break
                    # list_accountsを回りきったら例外アカウントと連携している
                    else:
                        print(principal['Principal']['AWS'])
                        print('ポリシー:開けすぎ？')
                        message += function['FunctionName'] + '：未確認アカウントとの連携があります。：' + principal['Principal']['AWS'] + '\n'
                # Principalの許可設定が'*'の場合は開けすぎ判定を出す
                elif '*' in principal['Principal']:
                    print('*')
                    print('ポリシー:開けすぎ？')
                    message += function['FunctionName'] + ':許可設定が広すぎます。：' + principal['Principal']['AWS'] + '\n'
        
        # リソースポリシーが無いときのエラーを回避            
        except client.exceptions.ResourceNotFoundException as e:
            pass
        
    print(message)