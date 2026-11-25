
class Event {
  final int id;
  final String title;
  final String description;
  final String location;
  final DateTime startDateTime;
  final DateTime endDateTime;
  final DateTime? registrationDeadline;
  final int? capacity;
  final int registeredCount;
  final int? remainingCapacity;
  final String? myRegistrationStatus;
  final String coverImageUrl;
  final String status;
  final int clubId;
  final String clubName;
  final String universityName;

  Event({
    required this.id,
    required this.title,
    required this.description,
    required this.location,
    required this.startDateTime,
    required this.endDateTime,
    this.registrationDeadline,
    this.capacity,
    required this.registeredCount,
    this.remainingCapacity,
    this.myRegistrationStatus,
    required this.coverImageUrl,
    required this.status,
    required this.clubId,
    required this.clubName,
    required this.universityName,
  });

  factory Event.fromJson(Map<String, dynamic> json) {
    return Event(
      id: json['id'] as int,
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      location: json['location'] ?? '',
      startDateTime: DateTime.parse(json['start_datetime']),
      endDateTime: DateTime.parse(json['end_datetime']),
      registrationDeadline: json['registration_deadline'] != null
          ? DateTime.parse(json['registration_deadline'])
          : null,
      capacity: json['capacity'],
      registeredCount: json['registered_count'] ?? 0,
      remainingCapacity: json['remaining_capacity'],
      myRegistrationStatus: json['my_registration_status'],
      coverImageUrl: json['cover_image_url'] ?? '',
      status: json['status'] ?? '',
      clubId: json['club'] as int,
      clubName: json['club_name'] ?? '',
      universityName: json['university_name'] ?? '',
    );
  }
}
