import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import RivalryMatch
from accounts.models import CustomUser
from exams.models import Question
import random

# صف انتظار بازیکنان
waiting_players = []

class RivalryConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_group_name = None
        self.match = None
        self.question_timer = None
        await self.accept()
        print(f"🟢 {self.user.display_name} متصل شد.")

    async def disconnect(self, close_code):
        # اگر کاربر توی صف بود، حذفش کن
        if self in waiting_players:
            waiting_players.remove(self)
            
        # اگر توی اتاق مسابقه بود، به حریف بگو
        if self.room_group_name:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'opponent_disconnected',
                    'message': 'حریف شما از مسابقه خارج شد.'
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        if self.question_timer:
            self.question_timer.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'find_match':
            await self.handle_matchmaking()
            
        elif action == 'submit_answer':
            await self.handle_answer(data.get('answer'))

    async def handle_matchmaking(self):
        # اگر کاربر از قبل توی صف هست، نادیده بگیر
        if self in waiting_players:
            return

        # اگر کسی توی صف هست، مسابقه رو شروع کن
        if waiting_players:
            opponent = waiting_players.pop(0)
            
            # ساخت مسابقه در دیتابیس
            self.match = await self.create_match(self.user, opponent.user)
            self.room_group_name = f"match_{self.match.id}"
            opponent.room_group_name = self.room_group_name
            opponent.match = self.match

            # جوین کردن هر دو نفر به گروه
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.channel_layer.group_add(self.room_group_name, opponent.channel_name)

            # شروع مسابقه برای هر دو
            await self.start_game(self)
            await self.start_game(opponent)
        else:
            # کاربر رو به صف اضافه کن
            waiting_players.append(self)
            await self.send(json.dumps({
                'type': 'waiting',
                'message': 'در حال جستجوی حریف...'
            }))

    async def start_game(self, player_consumer):
        # پیدا کردن یه سوال تصادفی
        question = await self.get_random_question()
        if not question:
            await player_consumer.send(json.dumps({'type': 'error', 'message': 'هیچ سوالی در بانک سوالات نیست!'}))
            return

        options = [
            question.option_1, question.option_2, 
            question.option_3, question.option_4
        ]

        await player_consumer.send(json.dumps({
            'type': 'match_found',
            'match_id': self.match.id,
            'opponent_name': player_consumer.scope['user'].display_name,
            'opponent_avatar': player_consumer.scope['user'].avatar.url if player_consumer.scope['user'].avatar else None,
            'question': {
                'id': question.id,
                'text': question.question_text,
                'options': options,
                'correct': question.correct_option
            }
        }))

        # شروع تایمر ۵۰ ثانیه‌ای (فقط برای پلیر اول تنظیم میشه تا دوبار اجرا نشه)
        if player_consumer == self:
            self.question_timer = asyncio.create_task(self.game_timer(question))

    async def game_timer(self, question):
        await asyncio.sleep(50) # 50 ثانیه فرصت
        # اگر تا 50 ثانیه کسی جواب نداد
        if self.room_group_name:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_over',
                    'winner': None,
                    'loser': None,
                    'reason': 'timeout'
                }
            )

    async def handle_answer(self, answer):
        if not self.room_group_name or not self.match:
            return

        # چون هر دو کاربرها توی گروه هستن، فقط نفر اولی که جواب بده برنده میشه
        # برای سادگی: اگه جواب درست بود برنده میشه، اگه غلط بود حریفش برنده میشه
        # نکته: در نسخه پیشرفته‌تر می‌تونیم تایمر هر کاربر رو جدا کنیم
        
        winner = self.user
        loser = await self.get_opponent(self.user)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_over',
                'winner_id': winner.id,
                'loser_id': loser.id,
                'winner_name': winner.display_name,
                'reason': 'answered'
            }
        )

    # --- توابع کمکی (دیتابیس) ---

    @database_sync_to_async
    def create_match(self, p1, p2):
        return RivalryMatch.objects.create(
            player1=p1, player2=p2, status='playing'
        )

    @database_sync_to_async
    def get_random_question(self):
        questions = list(Question.objects.all())
        if questions:
            return random.choice(questions)
        return None

    @database_sync_to_async
    def get_opponent(self, user):
        if self.match.player1 == user:
            return self.match.player2
        return self.match.player1

    # --- هندلرهای گروه ---

    async def opponent_disconnected(self, event):
        await self.send(json.dumps({
            'type': 'opponent_left',
            'message': event['message']
        }))
        # تایمر رو متوقف کن
        if self.question_timer:
            self.question_timer.cancel()
        
        # ثبت برد برای کسی که مونده
        await self.register_win_loss(self.user, await self.get_opponent(self.user))

    async def game_over(self, event):
        if self.question_timer:
            self.question_timer.cancel()

        # اگه winner_id ارسال شده باشه، دیتابیس رو آپدیت کن
        if event.get('winner_id'):
            winner = await self.get_user_by_id(event['winner_id'])
            loser = await self.get_user_by_id(event['loser_id'])
            await self.register_win_loss(winner, loser)

        await self.send(json.dumps({
            'type': 'game_over',
            'winner_name': event.get('winner_name', 'نامشخص'),
            'reason': event['reason']
        }))
        
        self.room_group_name = None # پایان مسابقه

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def register_win_loss(self, winner, loser):
        if winner and loser:
            winner.rivalry_wins += 1
            winner.points += 4
            winner.save()
            
            loser.rivalry_losses += 1
            loser.points -= 2
            loser.save()
            
            # آپدیت دیتابیس مسابقه
            match = RivalryMatch.objects.filter(status='playing').last()
            if match:
                match.status = 'finished'
                match.winner = winner
                match.finished_at = timezone.now()
                match.save()