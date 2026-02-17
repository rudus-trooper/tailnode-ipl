"""
Minimal IPL Auction Views
"""
from decimal import Decimal
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Team, Player


@api_view(['POST'])
def populate_data(request):
    """Populate database with realistic IPL teams and players"""
    
    # Clear existing data
    Team.objects.all().delete()
    Player.objects.all().delete()
    
    # Create 8 IPL Teams with ₹125 Crore purse
    teams_data = [
        {"name": "Mumbai Indians", "purse_remaining": 1250000000},
        {"name": "Chennai Super Kings", "purse_remaining": 1250000000},
        {"name": "Royal Challengers Bangalore", "purse_remaining": 1250000000},
        {"name": "Kolkata Knight Riders", "purse_remaining": 1250000000},
        {"name": "Delhi Capitals", "purse_remaining": 1250000000},
        {"name": "Rajasthan Royals", "purse_remaining": 1250000000},
        {"name": "Sunrisers Hyderabad", "purse_remaining": 1250000000},
        {"name": "Punjab Kings", "purse_remaining": 1250000000},
    ]
    
    teams = []
    for t in teams_data:
        team = Team.objects.create(**t)
        teams.append(team)
    
    # Create Capped Players (₹2 Crore base price)
    capped_players = [
        {"name": "Virat Kohli", "base_price": 20000000, "is_capped": True},
        {"name": "Rohit Sharma", "base_price": 20000000, "is_capped": True},
        {"name": "MS Dhoni", "base_price": 20000000, "is_capped": True},
        {"name": "Jasprit Bumrah", "base_price": 20000000, "is_capped": True},
        {"name": "Ravindra Jadeja", "base_price": 20000000, "is_capped": True},
        {"name": "Hardik Pandya", "base_price": 20000000, "is_capped": True},
        {"name": "KL Rahul", "base_price": 20000000, "is_capped": True},
        {"name": "Shubman Gill", "base_price": 20000000, "is_capped": True},
        {"name": "Rishabh Pant", "base_price": 20000000, "is_capped": True},
        {"name": "Sanju Samson", "base_price": 20000000, "is_capped": True},
        {"name": "Suryakumar Yadav", "base_price": 20000000, "is_capped": True},
        {"name": "Mohammed Shami", "base_price": 20000000, "is_capped": True},
        {"name": "Rashid Khan", "base_price": 20000000, "is_capped": True},
        {"name": "Andre Russell", "base_price": 20000000, "is_capped": True},
        {"name": "Pat Cummins", "base_price": 20000000, "is_capped": True},
    ]
    
    # Create Uncapped Players (₹30 Lakh base price)
    uncapped_players = [
        {"name": "Yashasvi Jaiswal", "base_price": 3000000, "is_capped": False},
        {"name": "Rinku Singh", "base_price": 3000000, "is_capped": False},
        {"name": "Tilak Varma", "base_price": 3000000, "is_capped": False},
        {"name": "Jitesh Sharma", "base_price": 3000000, "is_capped": False},
        {"name": "Nitish Rana", "base_price": 3000000, "is_capped": False},
        {"name": "Ravi Bishnoi", "base_price": 3000000, "is_capped": False},
        {"name": "Avesh Khan", "base_price": 3000000, "is_capped": False},
        {"name": "Arshdeep Singh", "base_price": 3000000, "is_capped": False},
        {"name": "Shivam Dube", "base_price": 3000000, "is_capped": False},
        {"name": "Rahul Tripathi", "base_price": 3000000, "is_capped": False},
    ]
    
    # Create all players
    players_created = []
    for p in capped_players + uncapped_players:
        player = Player.objects.create(**p, status='active')
        players_created.append(player)
    
    return Response({
        'message': 'Database populated successfully',
        'teams_created': len(teams),
        'players_created': len(players_created),
        'capped_players': len(capped_players),
        'uncapped_players': len(uncapped_players),
        'teams': [t.name for t in teams],
        'active_players': [p.name for p in players_created[:5]],
    })


@api_view(['GET'])
def player_list(request):
    """List all players"""
    players = Player.objects.all()
    data = [{
        'id': p.id,
        'name': p.name,
        'is_capped': p.is_capped,
        'base_price': str(p.base_price),
        'current_price': str(p.current_price) if p.current_price else None,
        'status': p.status,
    } for p in players]
    return Response(data)


@api_view(['GET'])
def active_player(request):
    """Get the currently active player for bidding"""
    try:
        player = Player.objects.filter(status='active').first()
        if not player:
            return Response({'error': 'No active player'}, status=404)
        return Response({
            'id': player.id,
            'name': player.name,
            'is_capped': player.is_capped,
            'base_price': str(player.base_price),
            'current_price': str(player.current_price) if player.current_price else None,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def place_bid(request, pk):
    """
    Place a bid on a player.
    Rules:
    - Bid must be higher than current price
    - Team must have sufficient purse
    - Player must be active
    """
    try:
        amount = Decimal(request.data.get('amount', 0))
        team_id = request.data.get('team_id')
        
        with transaction.atomic():
            player = Player.objects.select_for_update().get(pk=pk)
            team = Team.objects.select_for_update().get(pk=team_id)
            
            # Rule: Player must be active
            if player.status != 'active':
                return Response({'error': 'Bidding closed - player sold'}, status=403)
            
            # Rule: Bid must be higher than current price
            min_price = player.current_price or player.base_price
            if amount <= min_price:
                return Response({
                    'error': f'Bid too low. Must be > ₹{min_price:,.0f}'
                }, status=400)
            
            # Security Rule: Team cannot exceed purse_remaining
            if amount > team.purse_remaining:
                return Response({
                    'error': f'Insufficient purse. Available: ₹{team.purse_remaining:,.0f}'
                }, status=400)
            
            # Refund previous bidder
            if player.highest_bidder and player.highest_bidder != team:
                prev_team = Team.objects.select_for_update().get(pk=player.highest_bidder.pk)
                prev_team.purse_remaining += player.current_price
                prev_team.save()
            
            # Update bid
            team.purse_remaining -= amount
            team.save()
            
            player.current_price = amount
            player.highest_bidder = team
            player.save()
            
            return Response({
                'message': 'Bid placed successfully',
                'player': player.name,
                'current_price': f'{player.current_price:.2f}',
                'highest_bidder': team.name,
                'team_purse_remaining': f'{team.purse_remaining:.2f}',
            })
            
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=404)
    except Team.DoesNotExist:
        return Response({'error': 'Team not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def team_list(request):
    """List all teams with purse info"""
    teams = Team.objects.all()
    data = [{
        'id': t.id,
        'name': t.name,
        'purse_remaining': str(t.purse_remaining),
    } for t in teams]
    return Response(data)
