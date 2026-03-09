# Study Planner Presentation Script

## 5-Minute Code Walkthrough Script

Hi everyone, my name is Adam, and this is my project, **Study Planner**. For this walkthrough, I want to explain the code structure behind the app and how the main pieces work together.

I would start by explaining that this is a Django project, so the code follows a fairly standard structure. The main application logic lives in `planner/`, and the project-level configuration lives in `studyplanner/`. The easiest way to understand the app is to walk through it in the order Django uses it: models, views, forms, URLs, templates, and tests.

The first file I would open is `planner/models.py`. This file defines the main data structure for the app. There are three core models: `Course`, `Assignment`, and `StudyResource`. `Course` stores class information like course code, instructor, meeting schedule, syllabus details, and notes. `Assignment` belongs to a course and stores due date, status, priority, notes, and related resources. `StudyResource` stores learning materials like videos, articles, slides, and practice problems.

The most important relationship in this file is that assignments can be connected to many study resources through a many-to-many relationship. That relationship is what makes this more than a basic task tracker. It allows the app to connect actual study materials to the work a student needs to complete.

After that, I would move to `planner/views.py`, because this is where most of the application logic lives. The `HomeView` is a good example because it powers the dashboard. It takes assignments for the logged-in user and sorts them into overdue, due today, due this week, and high-priority sections. That view is a good example of how backend logic directly shapes the user experience.

I would also point out that the views consistently filter data by the logged-in user. For example, courses are filtered by `user=self.request.user`, and assignments are filtered through the related course owner. That matters because each user should only be able to see their own data.

Another important part of `views.py` is the create and update flow for assignments and study resources. The assignment views pass the logged-in user into the form so only that user’s resources appear as choices. The resource creation view also handles redirect logic so a user can create a resource while working on an assignment and then return to the correct place in the workflow.

Next, I would open `planner/forms.py`. This is a smaller file, but it is important because it customizes the form behavior. The main point I would mention is that `AssignmentForm` filters the `resources` field queryset by user. That prevents users from seeing resources they do not own and keeps the form behavior aligned with the authorization rules in the views.

Then I would go to `planner/urls.py`. This file is useful in a presentation because it gives a quick map of the whole app. You can see the routes for courses, assignments, resource creation, completion actions, and authentication-related pages. It gives a high-level picture of how the application is organized.

After the backend files, I would show a few templates. I would open `planner/templates/home.html` to connect the dashboard view logic to the actual UI. Then I would show `planner/templates/assignments/form.html` and `planner/templates/resources/form.html` because these templates are where the assignment-resource workflow becomes visible to the user.

That leads into the part I am most proud of, which is the resource creation flow during assignment creation. The reason I like talking about this part in code is that it touches several layers at once. The models define the relationship, the views manage the redirect logic, the forms control which resources appear, and the templates expose the workflow in the interface. It is a good example of how a seemingly small feature requires multiple parts of the codebase to work together correctly.

Finally, I would open `planner/tests.py`. This file shows that I tested the most important behaviors in the app, including authentication, course detail behavior, assignment completion, filtering, and resource creation. I think it is worth ending on tests because it shows that I not only built the features, but also verified that the critical user flows work correctly.

So if I had to summarize the codebase in one sentence, I would say: `models.py` defines the data, `views.py` defines the behavior, `forms.py` refines user input, `urls.py` maps the features, templates render the experience, and `tests.py` protects the key workflows.

## Code Walkthrough Order

1. `planner/models.py`
2. `planner/views.py`
3. `planner/forms.py`
4. `planner/urls.py`
5. `planner/templates/home.html`
6. `planner/templates/assignments/form.html`
7. `planner/templates/resources/form.html`
8. `planner/tests.py`

## What To Say By File

### `planner/models.py`

- This is the core data layer of the app.
- `Course`, `Assignment`, and `StudyResource` are the three main models.
- The many-to-many relationship between assignments and resources is one of the most important design choices.

### `planner/views.py`

- This file contains the main application logic.
- `HomeView` builds the dashboard sections.
- The views also enforce user-specific access and handle the assignment/resource creation flow.

### `planner/forms.py`

- This file customizes how forms behave.
- The key detail is that assignment resource choices are filtered to the logged-in user.

### `planner/urls.py`

- This is the route map for the app.
- It is a fast way to show the full feature set and how pages connect.

### `planner/templates/home.html`

- This template renders the dashboard UI.
- It reflects the categorized assignment logic from the view.

### `planner/templates/assignments/form.html`

- This is where assignment creation happens.
- It also gives the user a way to create a new resource during the assignment workflow.

### `planner/templates/resources/form.html`

- This template supports both normal resource creation and assignment-linked resource creation.
- It helps preserve the user’s place in the workflow.

### `planner/tests.py`

- This file verifies the most important application behaviors.
- It is where I check authentication, assignment actions, filtering, and resource flow behavior.

## Demo Order

1. Dashboard
2. Courses list
3. Course detail page
4. Assignment detail or assignment creation
5. Resource linking or resource creation
6. Resource library

## Most Proud Of / Most Challenging

The part of the project I am most proud of is the assignment-to-resource workflow, because it is a feature that crosses almost every important layer of the app.

If I were walking through the code for this feature, I would start in `planner/models.py`. The foundation is the `resources = models.ManyToManyField("StudyResource", blank=True, related_name="assignments")` field on the `Assignment` model. That line matters because it defines the relationship that makes the whole feature possible. An assignment can have multiple resources, and a resource can support multiple assignments. Without that relationship, resources would just be a separate list and not part of the actual study workflow.

After that, I would open `planner/forms.py`. In `AssignmentForm`, the `__init__` method filters `self.fields["resources"].queryset = StudyResource.objects.filter(user=user)`. That piece is important because it keeps the resource selector scoped to the logged-in user. From a technical standpoint, it solves two problems at once: it keeps the interface clean by only showing relevant resources, and it enforces ownership at the form level so users cannot attach another user’s resources.

The most important file for this feature is `planner/views.py`. In `AssignmentCreateView` and `AssignmentUpdateView`, the current user is passed into the form through `get_form_kwargs`, which is what allows the form-level filtering to work. In the create view, the code also adds the current course into template context so the assignment form can build the correct “Add New Resource” link even before an assignment exists.

Still in `planner/views.py`, the more challenging logic is in `StudyResourceCreateView`. That view has to support two different cases. The first case is when the user is creating a resource for an assignment that already exists. In that flow, `dispatch` finds the assignment from the URL, and `form_valid` attaches the newly created resource to that assignment. The second case is harder: the user is still on the new assignment page, so there is no saved assignment yet. In that case, the view uses a safe `next` value to remember where the user came from and sends them back to the assignment form after the resource is created.

That redirect handling is the part I found most challenging, because it is not just about saving the resource. The code has to preserve user flow. The `get_next_url` method validates the return path using `url_has_allowed_host_and_scheme`, which matters because redirects should not trust arbitrary input. Then `get_success_url` decides where to send the user after the resource is saved. If the resource came from an existing assignment, it returns to the assignment detail page. If it came from the new assignment flow, it returns to the assignment creation page. If neither applies, it falls back to the normal resource detail page.

The templates are also part of why I am proud of this feature. In `planner/templates/assignments/form.html`, the assignment form shows the `resources` field and also exposes an “Add New Resource” action. When editing an existing assignment, that link goes directly to the assignment-specific resource creation route. When creating a brand new assignment, the template builds a resource creation link with a `next` parameter that points back to the assignment form. That is what keeps the workflow connected instead of forcing the user to restart.

Then in `planner/templates/resources/form.html`, the resource form preserves that return path with a hidden `next` input. It also adjusts the cancel behavior based on context. If the resource is being created for an existing assignment, cancel returns to that assignment. If the user came from the new assignment form, cancel returns there instead. That means both save and cancel respect the workflow the user is already in.

I would also mention `planner/tests.py`, because I think this feature would be much weaker to present if it only worked manually. The tests cover both the existing-assignment flow and the new-assignment return flow. There are tests that confirm a resource can be created and attached to an assignment, that the assignment creation page links correctly to resource creation with a return URL, and that creating a resource with that return URL redirects the user back into the assignment workflow. For me, that is a strong example of taking a feature from “it seems to work” to “it is actually protected.”

The reason I am most proud of this section is that it combines model relationships, authorization-aware forms, view-level redirect logic, template behavior, and automated tests into one feature that actually improves the user experience. It looks small in the interface, but in the code it is a good example of full-stack problem solving.

## Proud Of Walkthrough Order

1. `planner/models.py`
2. `planner/forms.py`
3. `planner/views.py`
4. `planner/templates/assignments/form.html`
5. `planner/templates/resources/form.html`
6. `planner/tests.py`

## What To Say In The Proud Of Section

### `planner/models.py`

- The key line is the many-to-many relationship between assignments and resources.
- That relationship makes resources part of the assignment workflow instead of a separate feature.

### `planner/forms.py`

- The assignment form filters resource choices by the logged-in user.
- That keeps the form secure and user-specific.

### `planner/views.py`

- The assignment views pass the user into the form.
- The resource create view handles both existing-assignment and new-assignment flows.
- The `next` handling is the hardest part because it preserves workflow safely.

### `planner/templates/assignments/form.html`

- This template exposes the add-resource action right where the user needs it.
- It builds different links depending on whether the assignment already exists.

### `planner/templates/resources/form.html`

- This template preserves the return path with a hidden field.
- It also makes cancel behavior consistent with the user’s current workflow.

### `planner/tests.py`

- This file proves the flow works in both major cases.
- It is important because this feature depends on multiple moving parts working together.

## Quick Reminders

- Start already logged in
- Use seeded or prebuilt demo data
- Keep the demo moving and do not type more than necessary
- If something loads slowly, explain what the user is seeing and continue
- If you want a stronger technical presentation, use the code walkthrough section as your main script and keep the live demo short
