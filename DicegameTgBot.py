import telebot
from telebot import types
import mysql.connector
from mysql.connector import Error
import random


def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

global connection
connection = create_connection("localhost", "casino", "", "mini_casino")      #your database
bot = telebot.TeleBot('YOUR TOKEN')                                           #insert your telegram bot token

@bot.message_handler(commands=['start'])
def start(message):
    mess = f'<b>Hello</b> {message.from_user.first_name}'
    userid=message.from_user.id
    bot.send_message(message.chat.id, mess, parse_mode='html',reply_markup=None)
    datacon = connection.cursor()
    datacon.execute(f"SELECT id_telegram FROM clients WHERE id_telegram={userid};")
    myresult = datacon.fetchone()
    if (myresult==None):
        print("new client")
        query = f"INSERT INTO `clients`(`id_telegram`, `balance`) VALUES ({userid},0)"
        datacon = connection.cursor()
        datacon.execute(query)
        connection.commit()
        markup = types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = types.KeyboardButton('/game')
        itembtn2 = types.KeyboardButton('/start')
        itembtn3 = types.KeyboardButton('/myid')
        markup.add(itembtn1, itembtn2,itembtn3)
        bot.send_message(message.chat.id, f"youre balance: 0💵 \nFor deposits and withdrawals save youre ID and contact with @Aristocrat_DS", parse_mode='html',reply_markup=markup)
    else:
        datacon = connection.cursor()
        datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={userid};")
        markup = types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = types.KeyboardButton('/game')
        itembtn2 = types.KeyboardButton('/start')
        itembtn3 = types.KeyboardButton('/myid')
        markup.add(itembtn1, itembtn2,itembtn3)
        myresult = datacon.fetchone()
        bot.send_message(message.chat.id, f"Youre balance: {int(myresult[0])}💵\nFor deposits and withdrawals save youre ID and contact with @Aristocrat_DS", parse_mode='html',reply_markup=markup)


@bot.message_handler(commands=['myid'])
def checkid(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('/game')
    itembtn2 = types.KeyboardButton('/start')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, f"youre id:", parse_mode='html')
    bot.send_message(message.chat.id, f"{message.from_user.id}", parse_mode='html',reply_markup=markup)

@bot.message_handler(commands=['game'])
def game(message):
    userid=message.from_user.id
    datacon = connection.cursor()
    datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={userid};")
    myresult = datacon.fetchone()
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('10')
    itembtn2 = types.KeyboardButton('25')
    itembtn3 = types.KeyboardButton('50')
    itembtn4 = types.KeyboardButton('100')
    itembtn5 = types.KeyboardButton('250')
    itembtn6 = types.KeyboardButton('500')
    itembtn7 = types.KeyboardButton('1000')
    markup.row(itembtn1, itembtn2,itembtn3)
    markup.row(itembtn4, itembtn5,itembtn6)
    markup.row(itembtn7)
    msg=bot.send_message(message.chat.id, f"Youre balance: {int(myresult[0])}💵\nWhat bet?", parse_mode='html',reply_markup=markup)
    bot.register_next_step_handler(msg,stawka)
def stawka(message):
    if(message.text=="/game" or message.text=="/start"):
        print("eror")
    else:
        global cost
        cost=int(message.text)
        datacon = connection.cursor()
        datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
        myresult = datacon.fetchone()
        if (cost>int(myresult[0])or cost<0):
            markup = types.ReplyKeyboardMarkup(row_width=1)
            itembtn1 = types.KeyboardButton('/game')
            itembtn2 = types.KeyboardButton('/start')
            markup.add(itembtn1, itembtn2)
            bot.send_message(message.chat.id, f"No money", parse_mode='html',reply_markup=markup)
        else:
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtn1 = types.KeyboardButton('>3')
            itembtn3 = types.KeyboardButton('=3')
            itembtn2 = types.KeyboardButton('<3')
            markup.add(itembtn1, itembtn2,itembtn3)
            msg1=bot.send_message(message.chat.id, f"Choose or send ur number 1-6", parse_mode='html',reply_markup=markup)
            bot.register_next_step_handler(msg1,bet)


def bet(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    itembtn1 = types.KeyboardButton('/game')
    itembtn2 = types.KeyboardButton('/start')
    markup.add(itembtn1, itembtn2)
    rand=random.randrange(1,7)
    print(rand)
    if(message.text==">3"):
        if(rand>3):
            bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
            datacon = connection.cursor()
            datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
            myresult = datacon.fetchone()
            querywin = f"UPDATE `clients` SET `balance`= {int(myresult[0])+cost} WHERE id_telegram={message.from_user.id}"
            bot.send_message(message.chat.id,f"Balance: {int(myresult[0])+cost}💵")
            print(querywin)
            datacon.execute(querywin)
            connection.commit()
        else:
            bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
            datacon = connection.cursor()
            datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
            myresult = datacon.fetchone()
            querylose = f"UPDATE `clients` SET `balance`= {int(myresult[0])-cost} WHERE id_telegram={message.from_user.id}"
            bot.send_message(message.chat.id,f"Balance: {int(myresult[0])-cost}💵")
            print(querylose)
            datacon.execute(querylose)
            connection.commit()
    
    elif(message.text=="<3"):
        if(rand<3):
            bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
            datacon = connection.cursor()
            datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
            myresult = datacon.fetchone()
            querywin = f"UPDATE `clients` SET `balance`= {int(myresult[0])+cost} WHERE id_telegram={message.from_user.id}"
            bot.send_message(message.chat.id,f"Balance: {int(myresult[0])+cost}💵")
            print(querywin)
            datacon.execute(querywin)
            connection.commit()
        else:
            bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
            datacon = connection.cursor()
            datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
            myresult = datacon.fetchone()
            querylose = f"UPDATE `clients` SET `balance`= {int(myresult[0])-cost} WHERE id_telegram={message.from_user.id}"
            bot.send_message(message.chat.id,f"Balance: {int(myresult[0])-cost}💵")
            print(querylose)
            datacon.execute(querylose)
            connection.commit()
    
    elif(message.text=="=3"):
        if(rand==3):
            bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
            datacon = connection.cursor()
            datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
            myresult = datacon.fetchone()
            querywin = f"UPDATE `clients` SET `balance`= {int(myresult[0])+cost} WHERE id_telegram={message.from_user.id}"
            bot.send_message(message.chat.id,f"Balance: {int(myresult[0])+cost}💵")
            print(querywin)
            datacon.execute(querywin)
            connection.commit()
        else:
            bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
            datacon = connection.cursor()
            datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
            myresult = datacon.fetchone()
            querylose = f"UPDATE `clients` SET `balance`= {int(myresult[0])-cost} WHERE id_telegram={message.from_user.id}"
            bot.send_message(message.chat.id,f"Balance: {int(myresult[0])-cost}💵")
            print(querylose)
            datacon.execute(querylose)
            connection.commit()

    elif(int(message.text)==rand):
        bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
        datacon = connection.cursor()
        datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
        myresult = datacon.fetchone()
        querywin = f"UPDATE `clients` SET `balance`= {int(myresult[0])+cost*4} WHERE id_telegram={message.from_user.id}"
        bot.send_message(message.chat.id,f"Balance: {int(myresult[0])+cost*4}💵")
        print(querywin)
        datacon.execute(querywin)
        connection.commit()
    else:
        bot.send_sticker(message.chat.id,sticker(rand),reply_markup=markup)
        datacon = connection.cursor()
        datacon.execute(f"SELECT balance FROM clients WHERE id_telegram={message.from_user.id};")
        myresult = datacon.fetchone()
        querylose = f"UPDATE `clients` SET `balance`= {int(myresult[0])-cost} WHERE id_telegram={message.from_user.id}"
        bot.send_message(message.chat.id,f"Balance: {int(myresult[0])-cost}💵")
        print(querylose)
        datacon.execute(querylose)
        connection.commit()


def sticker(inprand):
    match inprand:
        case 1:
            return "CAACAgIAAxkBAAEEsAJieRDv5mEa55baNe_4eJlQshIIZgAC3MYBAAFji0YMsbUSFEouGv8kBA"
        
        case 2:
            return "CAACAgIAAxkBAAEEsAZieREBPif1wjOfNKfcpCiqt0Vn8QAC3cYBAAFji0YM608pO-wjAlEkBA"

        case 3:
            return "CAACAgIAAxkBAAEEsAhieREEWffBzrYDLU6oqctzUanJKAAC3sYBAAFji0YMVHH9hav7ILkkBA"
        
        case 4:
            return "CAACAgIAAxkBAAEEsApieREGDzKBdJTQpagsqRvW6ylnRwAC38YBAAFji0YMHEUTINW7YxckBA"
        
        case 5:
            return "CAACAgIAAxkBAAEEsAxieREIUnYX5ViUoY4e_h2epAF4CwAC4MYBAAFji0YMSLHz-sj_JqkkBA"
        
        case 6:
            return "CAACAgIAAxkBAAEEsA5ieREKmZqr1HQpzLEZeIQzy7rlMQAC4cYBAAFji0YM75p8zae_tHokBA"


@bot.message_handler()
def user_message(message):
    bot.send_message(message.chat.id, "I dont understand", parse_mode='html',reply_markup=None)
bot.polling(non_stop=True)
