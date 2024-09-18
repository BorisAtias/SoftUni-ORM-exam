from main_app.models import Astronaut, Mission, Spacecraft
from django.db.models import Count, F, Avg, Sum, Q


def get_astronauts(search_string=None):
    astronauts = Astronaut.objects.all()
    if search_string is not None:
        astronauts = astronauts.filter(Q(name__icontains=search_string) | Q(phone_number__icontains=search_string))
    astronauts = astronauts.order_by('name')
    if not astronauts.exists():
        return ""
    return "\n".join([f"Astronaut: {astronaut.name}, phone number: {astronaut.phone_number}, status: {'Active' if astronaut.is_active else 'Inactive'}" for astronaut in astronauts])

def get_top_astronaut():
    top_astronaut = Astronaut.objects.annotate(mission_count=Count('mission')).order_by('-mission_count', 'phone_number').first()
    if top_astronaut and top_astronaut.mission_count > 0:
        return f"Top Astronaut: {top_astronaut.name} with {top_astronaut.mission_count} missions."
    return "No data."

def get_top_commander():
    top_commander = Astronaut.objects.annotate(command_count=Count('missions_as_commander')).order_by('-command_count', 'phone_number').first()
    if top_commander and top_commander.command_count > 0:
        return f"Top Commander: {top_commander.name} with {top_commander.command_count} commanded missions."
    return "No data."


def get_last_completed_mission():
    last_mission = Mission.objects.filter(status='Completed').order_by('-launch_date').first()

    if last_mission:
        commander_name = last_mission.commander.name if last_mission.commander else 'TBA'
        astronauts_names = ", ".join(last_mission.astronauts.order_by('name').values_list('name', flat=True))
        total_spacewalks = last_mission.astronauts.aggregate(total=Sum('spacewalks'))['total'] or 0

        return (f"The last completed mission is: {last_mission.name}. "
                f"Commander: {commander_name}. "
                f"Astronauts: {astronauts_names}. "
                f"Spacecraft: {last_mission.spacecraft.name}. "
                f"Total spacewalks: {total_spacewalks}.")

    return "No data."

def get_most_used_spacecraft():
    most_used_spacecraft = Spacecraft.objects.annotate(mission_count=Count('mission')).order_by('-mission_count', 'name').first()
    if most_used_spacecraft and most_used_spacecraft.mission_count > 0:
        unique_astronauts = Astronaut.objects.filter(mission__spacecraft=most_used_spacecraft).distinct().count()
        return f"The most used spacecraft is: {most_used_spacecraft.name}, manufactured by {most_used_spacecraft.manufacturer}, used in {most_used_spacecraft.mission_count} missions, astronauts on missions: {unique_astronauts}."
    return "No data."

def decrease_spacecrafts_weight():
    spacecrafts = Spacecraft.objects.filter(mission__status='Planned', weight__gte=200.0).distinct()
    affected_spacecrafts_count = spacecrafts.update(weight=F('weight') - 200.0)
    if affected_spacecrafts_count > 0:
        avg_weight = Spacecraft.objects.aggregate(avg_weight=Avg('weight'))['avg_weight']
        return f"The weight of {affected_spacecrafts_count} spacecrafts has been decreased. The new average weight of all spacecrafts is {avg_weight:.1f}kg"
    return "No changes in weight."


